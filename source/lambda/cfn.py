import json
from datetime import datetime
import boto3

from botocore.exceptions import ClientError

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

cfn = boto3.client('cloudformation')

def delete_stack(stackName):
    logger.info(f'Deleting stack {stackName}')
    try:
        cfn.delete_stack(StackName=stackName)
        # Use delegated admin https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/stacksets-orgs-delegated-admin.html
    except Exception:
        logger.exception(f'Error while deleting the stack {stackName}')
        raise
    logger.debug(f'Initiated stack deletion for stack {stackName}') 

def process_ttl(stack, stackName, ttl):
    logger.info(f' Processing stack {stackName} for ttl {ttl}')
    try:
        stackCreationTime = stack['CreationTime'];
        print(stackCreationTime)

        now=datetime.utcnow()
        if(now.timestamp() > stackCreationTime.timestamp()):
            print(f'Now comparison {now.timestamp()} with {stackCreationTime.timestamp()}')
        
        lifeInSeconds=0;
        if(ttl[-1].lower()=='d'):
            lifeInSeconds=float(ttl[:-1])*24*3600;
            
        if(ttl[-1].lower()=='h'):
            lifeInSeconds=float(ttl[:-1])*3600;
        
        deleteTimeStamp=(stackCreationTime.timestamp() + lifeInSeconds)
        if(now.timestamp() < deleteTimeStamp):
            logger.info(f'{stackName} is ineligible for deletion due to {datetime.fromtimestamp(deleteTimeStamp)} is in future.')
            return;
        
        logger.info(f'{stackName} is eligible for deletion due to due to {datetime.fromtimestamp(deleteTimeStamp)} is in the past.')
        delete_stack(stackName);
        logger.info(f'{stackName} deletion initiated due to ttl {ttl}')

    except Exception:
        logger.exception('Error while parsing the ttl tag value')
        raise
    logger.info(f'Completed processing stack {stackName} for ttl {ttl}')        

def process_expire_after(stackName, expiryDate):
    logger.info(f' Processing stack {stackName} for expiryDate {expiryDate}')
    try:
        expiryDateObj = datetime.strptime(expiryDate, '%Y-%m-%d')
        present = datetime.now()
        if(expiryDateObj.date() > present.date()):
            logger.info(f'{stackName} is ineligible for deletion due to expiryDate {expiryDate} is in future.')
            return;
        
        logger.info(f'{stackName} is eligible for deletion due to expiryDate {expiryDate}')
        cfn.delete_stack(StackName=stackName);
        logger.info(f'{stackName} deletion initiated due to expiry date')

    except Exception:
        logger.exception('Error while parsing the date in YYYY-MM-DD format')
        raise
    logger.info(f'Completed processing stack {stackName} for expiryDate {expiryDate}')    


def parse_stacks():
    logger.info('Begin parsing stacks')
    try:
        paginator = cfn.get_paginator('list_stacks')
        response_iterator = paginator.paginate(
            StackStatusFilter=[
                'CREATE_FAILED','CREATE_COMPLETE','ROLLBACK_FAILED','ROLLBACK_COMPLETE','DELETE_FAILED','UPDATE_COMPLETE','UPDATE_FAILED','UPDATE_ROLLBACK_FAILED','UPDATE_ROLLBACK_COMPLETE','IMPORT_COMPLETE','IMPORT_ROLLBACK_FAILED','IMPORT_ROLLBACK_COMPLETE'
            ]
        )
        
        for page in response_iterator:
            for stackSummary in page['StackSummaries']:
                stackName=stackSummary['StackName']
                logger.debug(f'Parsing stack {stackSummary}')
                
                if 'ParentId' in stackSummary:
                    logger.debug('Skipping as this is a child stack')
                    continue
                
                stacksObj = cfn.describe_stacks(StackName=stackName)
                print('stackObj is ', stacksObj)
                stack=next((x for x in stacksObj['Stacks']), None)
                if 'Tags' not in stack:
                    logger.debug(f'No tags found for {stackObj}')
                    continue;
                
                for tag in stack['Tags']:
                    if tag["Key"] == 'ttl':
                        ttl=tag["Value"];
                        logger.info(f'Stack {stackName} has a ttl of {ttl}');
                        process_ttl(stack, stackName, ttl)
                    if tag["Key"] == 'expire-after':
                        expiryDate=tag["Value"];
                        logger.info(f'Stack {stackName} has an expiry date of {expiryDate}');
                        process_expire_after(stackName, expiryDate)

    except ClientError as e:
        logger.exception(f'Client error while checking stack : {e}')
        raise
    except Exception:
        logger.exception('Error while checking stack')
        raise
    logger.info('Completed parsing stacks')

def lambda_handler(event, context):
    logger.info('Resource deletion by tag function invoked.')
    
    cfn = boto3.resource('cloudformation')
    # parse_stacksets();
    parse_stacks();
    
    message='Resource deletion by tag function completed processing.'
    logger.info(message)
    return {
        'statusCode': 200,
        'body': json.dumps(message)
    }
