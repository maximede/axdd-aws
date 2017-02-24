from awslogin.aws import Consumer
import ConfigParser
import logging


# Uncomment to enable low level debugging
#logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    cfg = ConfigParser.ConfigParser()
    cfg.read('awslogin/settings.cfg')
    consumer = Consumer(cfg)
    consumer.store_credentials()

    print '\n\n----------------------------------------------------------------'
    print 'Your new access key pair has been stored in the AWS configuration file {0} under the saml profile.'.format(consumer.credentials_file)
    print 'Note that it will expire at {0}.'.format(consumer.token.credentials.expiration)
    print 'After this time, you may safely rerun this script to refresh your access key pair.'
    print 'To use this credential, call the AWS CLI with the --profile option (e.g. aws --profile saml ec2 describe-instances).'
    print '----------------------------------------------------------------\n\n'
