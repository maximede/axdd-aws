import boto.sts
import xml.etree.ElementTree as ET
import ConfigParser
from base64 import b64decode
from idp import IdentityProvider


class Consumer(object):
    def __init__(self, cfg):
        self.credentials_file = cfg.get('aws', 'credentials_file')
        self.region = cfg.get('aws', 'region')
	self.output_format = cfg.get('aws', 'output_format')
        self.role_arn = cfg.get('aws', 'role_arn')
        self.principal_arn = cfg.get('aws', 'principal_arn')
        self.token = None
        self.idp = IdentityProvider(cfg)

    def store_credentials(self):
        saml_assertion = self.idp.get_saml_assertion()
        if not (self.role_arn and self.principal_arn):
            self._set_role(saml_assertion)
        self._set_token(saml_assertion)
	self._write_config()

    def _write_config(self):
        config = ConfigParser.RawConfigParser()
        config.read(self.credentials_file)

        if not config.has_section('saml'):
            config.add_section('saml')

	config.set('saml', 'output', self.output_format)
        config.set('saml', 'region', self.region)
        config.set('saml', 'aws_access_key_id', self.token.credentials.access_key)
        config.set('saml', 'aws_secret_access_key', self.token.credentials.secret_key)
        config.set('saml', 'aws_session_token', self.token.credentials.session_token)

	with open(self.credentials_file, 'w+') as configfile:
            config.write(configfile)

    def _extract_aws_roles(self, saml_assertion):
        aws_roles = []
        root = ET.fromstring(b64decode(saml_assertion))
        for attr in root.iter('{urn:oasis:names:tc:SAML:2.0:assertion}Attribute'):
            if (attr.get('Name') == 'https://aws.amazon.com/SAML/Attributes/Role'):
                for value in attr.iter('{urn:oasis:names:tc:SAML:2.0:assertion}AttributeValue'):
                    aws_roles.append(value.text)
        return aws_roles

    def _set_role(self, saml_assertion):
        aws_roles = self._extract_aws_roles(saml_assertion)
        if len(aws_roles) == 1:
            (role_arn, principal_arn) = aws_roles[0].split(',')
        else:
            print ''
            print 'Please choose the role you would like to assume:'
            for idx, role in enumerate(aws_roles):
                print '[', idx, ']: ', role.split(',')[0]
            print 'Selection: ',
            selected_idx = raw_input()

            if int(selected_idx) > (len(aws_roles) - 1):
                print 'You selected an invalid role index, please try again'
                self._get_selected_role(saml_assertion)

            (role_arn, principal_arn) = aws_roles[int(selected_idx)].split(',')

        self.role_arn = role_arn
        self.principal_arn = principal_arn

    def _set_token(self, saml_assertion):
        conn = boto.sts.connect_to_region(self.region, anon=True)
        self.token = conn.assume_role_with_saml(
            self.role_arn, self.principal_arn, saml_assertion)
