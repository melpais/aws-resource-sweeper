# 🧹 aws-resource-sweeper

aws-resource-sweeper is an easy tool that helps you to automatically terminate your [AWS resources](#Supported-AWS-Resources) when you tag them with an expiry date or duration.

The tool helps you avoid unnecessary costs from forgetting to terminate resources that are no longer needed. 

## Be careful! 

Be aware that aws-resource-sweeper is a destructive tool and may delete important data. Be very careful when using it. We recommend only using the tool on non-production AWS accounts. 

To reduce the risks of accidents, we implemented safety precautions:

* We check the [Account Alias](https://docs.aws.amazon.com/IAM/latest/UserGuide/console_account-alias.html) of your AWS account to ensure that it does not contain `prod`. We recommend all your production AWS accounts to have the string (e.g. `mybusiness-prod`).
* By default, the tool will only automatically delete resources that are tagged to expire. To enforce tagging, you may need to [enforce tags using SCPs](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps_examples_tagging.html#example-require-tag-on-create).


## Example Use Cases

* **Experimentation:** Businesses are continously experimenting on AWS. You can use aws-resource-sweeper on your non-production AWS accounts to enable you to safely experiment with better guardrails on costs. 
* **Disaster Recovery (DR) Testing:** Businesses are often required to test their disaster recovery procedures periodically. When testing DR procedures, you can use aws-resource-sweeper on your DR accounts to ensure that resources are deleted when the procedure tests are done.  

## Instructions

- Deploy the tool to your non-production AWS accounts using clicking "Launch Stack" below. 
- When creating resources, ensure that you specify a tag for expiry. You can tag [supported resources](#Supported-AWS-Resources) with either: 
    * `ttl` in seconds (e.g. `ttl=600` for 10 minutes), or;
    *  `expires-after` in an epoch `yyyy-mm-dd` date format (e.g. `expires-after=2030-01-01`)
- The tool will then check these tags daily (at 12am epoch time) and automatically delete the resources accordingly.

## 1-Click Launch

[![Launch Stack](https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png)](https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?templateURL=https:%2F%2Fs3.amazonaws.com%2Fsolutions-reference%2Faws-instance-scheduler%2Flatest%2Faws-instance-scheduler.template&refid=sl_card)

IMPORTANT: Please ensure that you are logged in to the relevant non-production AWS account **and** region. By default, the link above will take you to the AWS `us-east-1` region. 

## Supported AWS Resources

* [CloudFormation Stacks](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/stacks.html)
* EC2 (Elastic Compute Cloud)
* RDS (Relational Database Service)

## FAQs

**How does the tool work?**

The tool is deployed as a collection of AWS resources using AWS CloudFormation. It consists of Lambdas which gets automatically triggered by an EventBridge rule that runs on a daily schedule. 

**It doesn't quite fit what I need. What should I do?**

We have designed the tool to be very simple. If you have any suggestions, feel free to raise an issue or contribute to the code repository. It's open-source! 

You can also try more advanced tools such as [aws-nuke](https://github.com/rebuy-de/aws-nuke) or [cdk-time-bomb](https://github.com/jmb12686/cdk-time-bomb). Note that these tools are 3rd party open source tools and are not affiliated with us or AWS in any way.

**How do I remove the tool from my account?**

The tool is deployed using CloudFormation. And so, to remove the tool, you can simply [delete the CloudFormation stack](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-console-delete-stack.html) and AWS will handle the termination of the collection of resources needed for the tool.

**Does this work with multiple AWS regions or accounts?**

The tool will need to be deployed to each region and each account. 
