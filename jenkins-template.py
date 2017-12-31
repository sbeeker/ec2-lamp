from troposphere import Ref, Template, Parameter, Output, Join, GetAtt, Base64
import troposphere.ec2 as ec2

t = Template()

# Security Group
# AMI ID and instance typ
# SSH key pair

sg = ec2.SecurityGroup("LampSg")
sg.GroupDescription = "Allow access through ports 22 and 80 to the WebServer"
sg.SecurityGroupIngress = [
	ec2.SecurityGroupRule(IpProtocol = "tcp", FromPort = "22", ToPort = "22", CidrIp = "0.0.0.0/32"),
	ec2.SecurityGroupRule(IpProtocol = "tcp", FromPort = "80", ToPort = "80", CidrIp = "0.0.0.0/32"),
	ec2.SecurityGroupRule(IpProtocol = "tcp", FromPort = "8080", ToPort = "8080", CidrIp = "0.0.0.0/32")
]
t.add_resource(sg)

# Lets add the SSH Key Pair as a Parameter
keypair = t.add_parameter(Parameter(
	"KeyName",
	Description = "Name of the SSH key pair that will be used to access the instance",
	Type = "String"
	))

instance = ec2.Instance("Jenkins")
instance.ImageId = "ami-55ef662f"
instance.InstanceType = "t2.micro"
instance.SecurityGroups = [Ref(sg)]
instance.KeyName = Ref(keypair)

t.add_resource(instance)

t.add_output(Output(
	"InstanceAccess",
	Description = "Command to use instance using SSH",
	Value = Join("", ["ssh -i ~/.ssh/Lampkey.pem ec2_user@", GetAtt(instance,"PublicDnsName")])
	   ))
t.add_output(Output(
	"WebUrl",
	Description = "The Url of the Web Server",
	Value = Join("", ["http://", GetAtt(instance,"PublicDnsName")])
	   ))

ud = Base64(Join('\n',
	[  
		"#!/bin/bash", 
		"sudo yum -y install httpd", 
		"sudo echo '<html><body><h1>Welcome to DevOps on AWS</h1></body></html>' > /var/www/html/test.html", 
		"sudo service httpd start", 
		"sudo chkconfig httpd on"  
	]))
instance.UserData = ud

print(t.to_json())
