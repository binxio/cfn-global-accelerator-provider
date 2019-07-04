# Custom::GlobalAccelerator resource provider
The `Custom::GlobalAccelerator` resource type provides an AWS Global Accelerator.`

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

## Return values
References to a resource will return the Accelerator ARN.

With 'Fn::GetAtt' the following values are available:

- `IPAddresses` - list of IP addresses of the global accelerator

## Caveats
When AWS finally provides official CloudFormation support, you will loose the ip addresses associated with 
the global accelerator creating using this Custom provider.  


