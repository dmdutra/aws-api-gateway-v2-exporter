import boto3
from dataclasses import dataclass
from prometheus_client import Gauge
from concurrent.futures import ThreadPoolExecutor

@dataclass
class PromMetrics:
    """
    A class that defines Prometheus metrics for AWS API Gateway metrics.

    This class uses the `prometheus_client.Gauge` to expose various API Gateway metrics 
    related to request count, latency, error counts, and error percentages. It supports 
    concurrent fetching of these metrics for multiple API Gateway routes using a 
    `ThreadPoolExecutor` to maximize efficiency.

    Prometheus metrics:
    -------------------
    - `count`: A Gauge metric that tracks the total request count for each API Gateway route.
    - `latency`: A Gauge metric that tracks the average latency for each API Gateway route.
    - `integration_latency`: A Gauge metric that tracks the average integration latency for each API Gateway route.
    - `count_5xx`: A Gauge metric that tracks the number of 5xx errors for each API Gateway route.
    - `count_4xx`: A Gauge metric that tracks the number of 4xx errors for each API Gateway route.
    - `error_percent`: A Gauge metric that tracks the error percentage (5xx + 4xx errors / total requests) for each API Gateway route.
    
    """
    
    count = Gauge('count', 'Request count', ['route'])
    latency = Gauge('Latency', 'Api gateway latency', ['route'])
    integration_latency = Gauge('IntegrationLatency', 'Api gateway integration latency', ['route'])
    count_5xx = Gauge('count_5xx', 'Api gateway 5xx errors', ['route'])
    count_4xx = Gauge('count_4xx', 'Api gateway 4xx errors', ['route'])
    error_percent = Gauge('error_percent', 'Api gateway error percent', ['route'])

    def prometheus_metrics(self, apigw, max_workers):
        """
        Fetches and updates Prometheus metrics for all routes in the specified API Gateway.

        This method retrieves key API Gateway metrics such as request counts, latency, 
        integration latency, 4xx and 5xx error counts, and error percentages for each route. 
        The metrics are then exposed via Prometheus using the appropriate labels.

        The method uses a `ThreadPoolExecutor` to retrieve metrics concurrently, optimizing 
        the process of collecting data for potentially large numbers of routes.

        Parameters:
        -----------
        apigw : ApiGatewayMetrics
            An instance of the `ApiGatewayMetrics` class, used to retrieve the metrics 
            for each route in the API Gateway.
        
        max_workers : int
            The maximum number of concurrent threads to use for fetching metrics. 
            A higher number of workers allows for more parallelism but also uses more 
            system resources.

        Returns:
        --------
        None
            This method does not return any value. It updates the Prometheus metrics 
            in-place.
        """

        routes = apigw.list_routes()
        process = []

        # Use a ThreadPoolExecutor to fetch metrics concurrently for each route
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for route in routes:
                route_key = route.get('RouteKey')
                method = route.get('Method')

                # Request count metric
                process.append(executor.submit(
                    self.count.labels(route=route_key).set(
                        apigw.get_route_statistics(
                            method, route_key, 'Sum', 'Count'
                        )
                    )
                ))

                # Latency metric
                process.append(executor.submit(
                    self.latency.labels(route=route_key).set(
                        apigw.get_route_statistics(
                            method, route_key, 'Average', 'Latency'
                        )
                    )
                ))

                # Integration latency metric
                process.append(executor.submit(
                    self.integration_latency.labels(route=route_key).set(
                        apigw.get_route_statistics(
                            method, route_key, 'Average', 'IntegrationLatency'
                        )
                    )
                ))

                # 5xx error count metric
                process.append(executor.submit(
                    self.count_5xx.labels(route=route_key).set(
                        apigw.get_route_statistics(
                            method, route_key, 'Sum', '5xx'
                        )
                    )
                ))

                # 4xx error count metric
                process.append(executor.submit(
                    self.count_4xx.labels(route=route_key).set(
                        apigw.get_route_statistics(
                            method, route_key, 'Sum', '4xx'
                        )
                    )
                ))

                # Error percentage metric
                process.append(executor.submit(
                    self.error_percent.labels(route=route_key).set(
                        apigw.error_percent(method, route_key)
                    )
                ))

