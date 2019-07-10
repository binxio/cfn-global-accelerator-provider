# Custom::GlobalAcceleratorEndpointGroup resource provider
The `Custom::GlobalAcceleratorEndpointGroup` resource type provides an AWS Global Accelerator endpoint group.

## Syntax
To create a global accelerator endpoint group in AWS CloudFormation template, use the following syntax:

```yaml
EndpointGroup:
  Type: Custom::GlobalAcceleratorEndpointGroup
  Properties:
    ServiceToken: !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:cfn-global-accelerator-provider'
    ListenerArn: !Ref GlobalAcceleratorListener
    TrafficDialPercentage: !Ref TrafficPercentage
    EndpointGroupRegion: !Ref AWS::Region
    EndpointConfigurations:
      - EndpointId: !Ref LoadBalancer
        Weight: 100
```

You can pass in all the arguments as specified by [CreateEndpointGroup](https://docs.aws.amazon.com/global-accelerator/latest/api/API_CreateEndpointGroup.html).

## Return values
References to a resource will return the Accelerator ARN.

## Caveats
If you wish to configure the endpoint group in a CloudFormation template that is deployed in the same region as your endpoint, you
need to deploy the custom global accelerator provider in that region too. CloudFormation does not allow us to call the 
provider across regions. 
