# Custom::GlobalAccelerator resource provider
The `Custom::GlobalAccelerator` resource type provides an AWS Global Accelerator.`

deprecated: use the official [AWS::GlobalAccelerator:Accelerator](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-globalaccelerator-accelerator.html) instead.

## Syntax
To create a global accelerator in AWS CloudFormation template, use the following syntax:

```yaml
Accelerator:
  Type: Custom::GlobalAccelerator
  Properties:
    Name: String
    Enabled: true
    IpAddressType: String
    ServiceToken: !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:cfn-global-accelerator-provider'
```

You can pass in all the arguments as specified by [CreateAccelerator](https://docs.aws.amazon.com/global-accelerator/latest/api/API_CreateAccelerator.html) except the IdempotencyToken.

## Return values
References to a resource will return the Accelerator ARN.

With 'Fn::GetAtt' the following values are available:

- `IPAddresses` - array of IP addresses of the global accelerator

## Caveats
- The global accelerator polls until the global accelerator is deployed and may exceed the lambda maximum timeout of 15 minutes.
