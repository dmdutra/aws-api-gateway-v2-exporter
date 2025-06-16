import boto3
import datetime

class ApiGatewayMetrics:
    """
    A class to interact with AWS API Gateway and retrieve relevant metrics from CloudWatch.

    This class provides methods to fetch statistics for API Gateway routes, including 
    metrics such as error rates (5xx, 4xx) and total request counts. The class uses the 
    AWS SDK (boto3) to access CloudWatch metrics and supports a customizable region and stage.
    """

    def __init__(self, api_id, stage, region="us-east-1"):
        """
        Initializes the ApiGatewayMetrics object with the provided API Gateway ID, stage, 
        and AWS region.

        Parameters:
        -----------
        api_id : str
            The ID of the API Gateway for which metrics are being fetched.
        
        stage : str
            The stage of the API Gateway (e.g., 'prod', 'dev').
        
        region : str, optional
            The AWS region where the API Gateway is located (default is 'us-east-1').
        """

        self._api_id = api_id
        self._stage = stage
        self._region = region

    def _aws_client(self, resource):
        """
        Creates and returns a boto3 client for a specified AWS resource.

        Parameters:
        -----------
        resource : str
            The AWS service resource to create a client for (e.g., 'cloudwatch', 'apigatewayv2').

        Returns:
        --------
        boto3.client
            The boto3 client for the specified AWS resource.
        """
        
        return boto3.client(resource, region_name=self._region)

    def get_route_statistics(self, method, resource, statistic, metric_name):
        """
        Fetches a specific metric statistic for a given API Gateway route from CloudWatch.

        Parameters:
        -----------
        method : str
            The HTTP method (e.g., 'GET', 'POST') of the API route.
        
        resource : str
            The resource path (e.g., '/users', '/products').
        
        statistic : str
            The type of statistic to retrieve (e.g., 'Sum', 'Average').
        
        metric_name : str
            The name of the metric to fetch (e.g., '5xx', 'Count').

        Returns:
        --------
        float
            The value of the requested metric statistic for the route, or 0 if no data is found.
        """

        client = self._aws_client('cloudwatch')

        end = datetime.datetime.utcnow()
        start = end - datetime.timedelta(minutes=1)

        dims = [
            {
                "Name": "ApiId",
                "Value": self._api_id
            },
            {
                "Name": "Method",
                "Value": method,
            },
            {
                "Name": "Resource",
                "Value": resource
            },
            {
                "Name": "Stage",
                "Value": self._stage
            }
        ]

        res = client.get_metric_statistics(
            Namespace="AWS/ApiGateway",
            MetricName=metric_name,
            Dimensions=dims,
            StartTime=start,
            EndTime=end, 
            Period=60,
            Statistics=[statistic]
        )

        try:
            datapoints = res.get('Datapoints')
            datapoint = datapoints[-1].get(statistic)
        except IndexError:
            datapoint = 0

        return datapoint

    def error_percent(self, method, resource):
        """
        Calculates the error percentage for a specific API Gateway route (method and resource).

        The error percentage is calculated as:
            (5xx error count + 4xx error count) / Total request count * 100

        Parameters:
        -----------
        method : str
            The HTTP method (e.g., 'GET', 'POST') of the API route.
        
        resource : str
            The resource path (e.g., '/users', '/products').

        Returns:
        --------
        float
            The percentage of errors (4xx + 5xx) out of total requests, or 0 if no data is found.
        """

        count_5xx = self.get_route_statistics(method, resource, 'Sum', '5xx')
        count_4xx = self.get_route_statistics(method, resource, 'Sum', '4xx')
        count = self.get_route_statistics(method, resource, 'Sum', 'Count')

        try:
            percent = (count_5xx + count_4xx) * 100 / count
        except ZeroDivisionError:
            percent = 0
        
        return percent

    def list_routes(self):
        """
        Lists all the routes (HTTP methods and corresponding paths) for the specified API Gateway.

        This method uses the API Gateway v2 client to retrieve route information.

        Returns:
        --------
        list
            A list of dictionaries containing HTTP methods and route paths for each route in the API Gateway.
        """

        client = self._aws_client('apigatewayv2')
        items = client.get_routes(ApiId=self._api_id).get('Items')

        routes = []

        for item in items:
            routes.append({
                'Method': item.get('RouteKey').split()[0],
                'RouteKey': item.get('RouteKey').split()[1],
            })

        return routes

