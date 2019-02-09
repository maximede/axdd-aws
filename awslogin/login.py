from awslogin.aws import CredentialsProvider
import logging


def login():
    # Uncomment to enable low level debugging
    # logging.basicConfig(level=logging.DEBUG)

    client = CredentialsProvider()
    client.get_credentials()

    print('\n\n----------------------------------------------------------------')
    print('Your new access key pair has been stored in the AWS configuration file {0} under the saml profile.'.format(client.credentials_file))
    print('The credentials will expire at {0}.'.format(client.token.credentials.expiration))
    print('To use these credentials, call the AWS CLI with the --profile option (e.g. aws --profile saml ec2 describe-instances).')
    print('----------------------------------------------------------------\n\n')

if __name__ == '__main__':
    login()
