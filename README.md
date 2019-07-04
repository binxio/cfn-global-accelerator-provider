# cfn-global-accelator-provider
AWS Global Accellator is an awesome service which was announced at on November 26, 2018 but helas without CloudFormation support.

This provider was created within a relaxed working day and allows you to create accelerators, listeners and endpoint groups in CloudFormation.

### How do I use it?
Very simple, add a custom global accelerator, listener and endpoint group as shown below:

```
Resources:
  Accelerator:
    Type: Custom::GlobalAccelerator
    Properties:
      Name: my-global-accelerator
      Enabled: true
      IpAddressType: IPV4
      ServiceToken: !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:cfn-global-accelerator-provider'

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

  EndpointGroup:
    Type: Custom::GlobalAcceleratorEndpointGroup
    Properties:
      ListenerArn: !Ref Listener
      EndpointGroupRegion: !Ref AWS::Region
      EndpointConfigurations:
       - EndpointId: !Ref LB
         Weight: 100
      ServiceToken: !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:cfn-global-accelerator-provider'

   LB:
    Type: AWS::ElasticLoadBalancer:
```


### Deploy the provider
To deploy the provider, type:

```sh
export AWS_REGION=us-west-2
aws cloudformation create-stack \
        --capabilities CAPABILITY_IAM \
        --stack-name cfn-global-accelerator-provider \
        --template-body file://./cloudformation/cfn-resource-provider.yaml

aws cloudformation wait stack-create-complete  --stack-name cfn-global-accelerator-provider
```

This CloudFormation template will use our pre-packaged provider from `s3://binxio-public/lambdas/cfn-global-accelerator-provider-latest.zip`.

### Deploy the demo
In order to deploy the demo, type:

```sh
cd cloudformation
sceptre  launch -y demo
```
