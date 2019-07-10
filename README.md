# cfn-global-accelator-provider
AWS Global Accelerator is an awesome service which was announced at on November 26, 2018 but helas without CloudFormation support. This provider 
was created within a relaxed working day and allows you to configure your accelerators, listeners and endpoint groups in CloudFormation.

<!--more-->
### How do I use it?
Very simple, add a custom [global accelerator](docs/global-accelerator.md), [listener]((docs/global-accelerator-listener.md) and one or
more [endpoint groups]((docs/global-accelerator-endpoint-group.md) as shown below:

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
```

Using the Listener ARN, you can now add endpoint groups to point to your regional resources:

```
  EndpointGroup:
    Type: Custom::GlobalAcceleratorEndpointGroup
    Properties:
      ServiceToken: !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:cfn-global-accelerator-provider'
      ListenerArn: !Ref GlobalAcceleratorListener
      EndpointGroupRegion: !Ref AWS::Region
      EndpointConfigurations:
        - EndpointId: !Ref LoadBalancer
          Weight: 100

  LoadBalancer:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Properties:
      Subnets: !Ref PublicSubnets
      SecurityGroups:
      - !Ref ALBSecurityGroup
```

-### Deploy the provider
To deploy the provider, type:

```sh
git clone https://github.com/binxio/cfn-global-accelerator-provider.git
cd cfn-global-accelerator-provider
aws --region us-west-2 \
    cloudformation create-stack \
        --capabilities CAPABILITY_IAM \
        --stack-name cfn-global-accelerator-provider \
        --template-body file://./cloudformation/templates/provider.yaml

aws --region us-west-2 cloudformation wait stack-create-complete  --stack-name cfn-global-accelerator-provider
```

This CloudFormation template will use our pre-packaged provider from `s3://binxio-public/lambdas/cfn-global-accelerator-provider-0.1.1.zip`.


### Demo
The following tree shows the deployment configuration of our global accelerator demo:
```
demo
└── us-west-2
    ├── accelerator.yaml
│   ├── provider.yaml
├── eu-central-1
│   ├── app.yaml
│   ├── provider.yaml
│   └── vpc.yaml
├── eu-west-1
│   ├── app.yaml
│   ├── provider.yaml
│   └── vpc.yaml
```
The accelerator is deployed in us-west-2 and the application is deployed in both eu-central-1 and eu-west-1 respectively. The
custom provider also needs to be deployed in these regions in order to create the global accelerator endpoint groups.

### Deploy the demo
In order to deploy the demo, type:

```sh
cd cloudformation
pip install sceptre
sceptre launch -y demo
```

to view the application, type:`

```sh
GA_IP_ADDRESS=$(
  aws --region us-west-2 globalaccelerator \
  list-accelerators \
    --output text \
    --query 'Accelerators[?Name==`cfn-global-accelerator-demo-us-west-2-accelerator`].IpSets[0].IpAddresses[0]')

open http://$GA_IP_ADDRESS
```

## Conclusion
This provider was created within a relaxed working day and allows you to configure your accelerators, listeners and endpoint groups in CloudFormation.
Although creating this temporary custom provider cost less than a day, it is not the ideal solution. It has to be created, installed and decommissioned when Amazon finally provides support for the Global Accelerator resources.
`
If it helps, I would like to offer AWS our services to ensure that CloudFormation is always on-par with the API before the feature is released.
