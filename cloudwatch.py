import time
import boto3

sqs_client = boto3.resource('sqs', region_name='eu-north-1')
asg_client = boto3.client('autoscaling', region_name='eu-north-1')
cloudwatch = boto3.client('cloudwatch', region_name='eu-north-1')

AUTOSCALING_GROUP_NAME = 'nancyf_yolo5_asg'
QUEUE_NAME = 'nancyf_queue'
while True:
    queue = sqs_client.get_queue_by_name(QueueName=QUEUE_NAME)
    msgs_in_queue = int(queue.attributes.get('ApproximateNumberOfMessages'))
    asg_groups = asg_client.describe_auto_scaling_groups(AutoScalingGroupNames=[AUTOSCALING_GROUP_NAME])[
        'AutoScalingGroups']
    if not asg_groups:
        raise RuntimeError('Autoscaling group not found')
    else:
        asg_size = asg_groups[0]['DesiredCapacity']

    backlog_per_instance = msgs_in_queue / asg_size

    # TODO: Send backlog_per_instance to CloudWatch using put-metric-data API
    cloudwatch.put_metric_data(
        Namespace='CustomMetrics_nancyf',
        MetricData=[
            {
                'MetricName': 'BacklogPerInstance',
                'Value': backlog_per_instance,
                'Unit': 'Count',
                'Dimensions': [
                    {
                        'Name': 'AutoScalingGroupName',
                        'Value': AUTOSCALING_GROUP_NAME
                    }
                ]
            }
        ]
    )
    time.sleep(30)
