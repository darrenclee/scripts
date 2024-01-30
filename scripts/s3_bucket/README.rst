S3 cleanup tool
===================

S3 tool that can be used remove objects from a bucket that has passed a x amount of days. 

.. contents:: :local:

Prerequisites
-------------

.. code-block:: bash

    1.  Start a virtualenv(optional)
    2.  Run "pip install -r requirements.txt".
    3.  For local dev, aws profile name can be passed into the script. 
    4.  Credentials can be also passed in and used depending on precedence.


Usage
-----

To use, run "python s3_cleanup.py" from the scripts/s3_cleanup folder. 

S3 cleanup tool command
-----------------------


.. code-block:: bash

  usage: s3_cleanup.py [-h] [-d DAYS] [-p PROFILE]

  S3 cleanup tool to remove objects older than a X number of days

  optional arguments:
    -h, --help            show this help message and exit
    -d DAYS, --days DAYS  How many days from current date to remove s3 objects
    -p PROFILE, --profile PROFILE
                          aws profile name

Example S3 cleanup command
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

  python s3_cleanup.py --days 5 --profile infra_lab_1

This will cleanup s3 bucket folders and objects that are 5 days passed
since current time of when this command was excuted.


Workflow
--------

1. Prepare your workspace with a virtualenv https://docs.python.org/3/tutorial/venv.html
2. Checks for credentials
    * Set AWS credentials by passing in profile name or using ways to pass in.
    * Note credentials precendence https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-authentication.html#cli-chap-authentication-precedence 
    * assume a role in your config list, using granted.dev https://www.granted.dev/
3. S3 cleanup tool
    * list all buckets in the account
    * retrieve a list of buckets with objects and folders according to days passed(default:365 days)
    * deletes all objects and folders according to days passed


Automate and deploy to prod
-----------------------------------------------------------------------------------
Eventbridge rule -> Lambda function

1. Complete all testing in lower enviromments before prod deployment

Permissions
  * Create a role for the lambda function
  * Policy with least privledge access to perform actions on a list of s3 buckets

Lambda
  * package the python and deploy lambda

Eventbridge rule 
  * create a rule to run on a schedule
  * rule with target to lambda function
  * rule to pass in env vars to lambda 


Notes/Todo
-----------------------------------------------------------------------------------
1. Configure S3 lifecycle policy

  * s3 lifecycle policy can accomplish the same task
  * update s3 bucket to allow a feature flag to enable lifecycle policy
  * lifecycle policy enabled in a bucket to expire objects or move them to archive s3 class

2. Add a safeguard for buckets to exclude

  * allow a list of bucket names to exclude
  * buckets in the list will not be set in the delete_object_dict

3. Add more logging

  * depending on amount of object, output could be too noisy
  * output to a file? 

4. Default for days set to 365, can be changed to required argument to force user input or env vars

5. Build a base docker image for future scripts, add a Makefile that will run checks(lint, pylint, tflint, unit tests, etc) in the container

6.  Add additional scripts to a lib folder. Decouple any repeatable functions, add common functions
such as the resource dict returned when describing AWS resources. 



Questions
-----------------------------------------------------------------------------------
1. Script can be run locally for dev/stage testing passing using local credentials. 
If deployed to prod, will need to add additional safeguard using IAM policy and a blocklist of buckets.

2. Add tests that will mock s3, add to pipeline to test before allowing any updates to this script

3. Add another argument for Y. Update get_buckets_with_objects_to_delete() object loop, check when list of objects is >= Y of deploys,
once it reached Y it will break out of loop for that bucket and move to the next bucket. We can also add
a new function that will sort the list of obj if needed, only return Y number of newest deploys.

