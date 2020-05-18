# Custom::GlobalAcceleratorListener resource provider
The `Custom::GlobalAcceleratorListener` resource type provides an AWS Global Accelerator listener.

deprecated: use the official [AWS::GlobalAccelerator::Listener](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-globalaccelerator-listener.html) instead.

## Syntax
To create a global accelerator listener in AWS CloudFormation template, use the following syntax:

```yaml
Listener:
  Type: Custom::GlobalAcceleratorListener
  Properties:
    AcceleratorArn: !Ref Accelerator
    Protocol: TCP
    PortRanges:
      - FromPort: 80
        ToPort: 80
    ClientAffinity: NONE
    ServiceToken: !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:cfn-global-accelerator-provider'
```

You can pass in all the arguments as specified by [CreateListener](https://docs.aws.amazon.com/global-accelerator/latest/api/API_CreateListener.html) except the IdempotencyToken.

## Return values
References to a resource will return the Accelerator ARN.
