from labScript import *
from apicPython import createVcenterDomain
from apicPython import createAttachableAccessEntityprofile
from apicPython import configureInterfacePcAndVpc
from apicPython import createAccessPortPolicyGroup
from apicPython import createVlanPool
from apicPython import createVcenterCredential
from apicPython import createVcenterController


class LabCreatingAvCenterDomainProfile(LabScript):

    def __init__(self):
        self.description = 'Create a vCenter Domain Profile'
        self.vcenter_domain = None
        self.vcenter_provider = None
        self.attachable_entity_profile = {}
        self.configured_interfaces_pc_vpc = {}
        self.vlan = {}
        self.vcenter_credential = {}
        self.vcenter_controller = {}
        super(LabCreatingAvCenterDomainProfile, self).__init__()

    def run_yaml_mode(self):
        super(LabCreatingAvCenterDomainProfile, self).run_yaml_mode()
        self.vcenter_domain = self.args['vcenter_domain']
        self.vcenter_provider = self.args['vcenter_provider']
        self.attachable_entity_profile = self.args['attachable_entity_profile']
        self.configured_interfaces_pc_vpc = self.args['configured_interfaces_pc_vpc']
        self.vlan = self.args['vlan']
        self.vcenter_credential = self.args['vcenter_credential']
        self.vcenter_controller = self.args['vcenter_controller']

    def wizard_mode_input_args(self):
        self.vcenter_provider, self.vcenter_domain = createVcenterDomain.input_key_args()
        self.attachable_entity_profile['name'] = createAttachableAccessEntityprofile.input_key_args()
        self.attachable_entity_profile['optional_args'] = createAttachableAccessEntityprofile.input_optional_args()
        self.configured_interfaces_pc_vpc['switch_profile'], self.configured_interfaces_pc_vpc['switches'], self.configured_interfaces_pc_vpc['interface_type'], self.configured_interfaces_pc_vpc['interface_ports'], self.configured_interfaces_pc_vpc['interface_selector'], self.configured_interfaces_pc_vpc['interface_policy_group'] = configureInterfacePcAndVpc.input_key_args()
        self.vlan['vlan_name'], self.vlan['vlan_mode'], self.vlan['range_from'], self.vlan['range_to'] = createVlanPool.input_key_args()
        self.vcenter_credential['profile'], self.vcenter_credential['vmm_user'], self.vcenter_credential['vmm_password'] = createVcenterCredential.input_key_args()
        self.vcenter_controller['name'], self.vcenter_controller['host_or_ip'], self.vcenter_controller['data_center'] = createVcenterController.input_key_args()
        self.vcenter_controller['optional_args'] = createVcenterController.input_optional_args()

    def main_function(self):

        # create Vlan Pool
        self.look_up_mo('uni/infra','')
        createVlanPool.create_vlan_pool(self.mo, self.vlan['vlan_name'], self.vlan['vlan_mode'], self.vlan['range_from'], self.vlan['range_to'])
        self.commit_change()

        # create Access Port Policy Group
        self.look_up_mo('uni/infra/funcprof/', '')
        createAccessPortPolicyGroup.create_access_port_port_policy_group(self.mo, self.configured_interfaces_pc_vpc['interface_policy_group'], optional_args={'entity_profile': self.attachable_entity_profile['name']})
        self.commit_change()

        # configure Interface PC and VPC
        self.look_up_mo('uni/infra', '')
        configureInterfacePcAndVpc.configure_interface_pc_and_vpc(self.mo, self.configured_interfaces_pc_vpc['switch_profile'], self.configured_interfaces_pc_vpc['switches'], self.configured_interfaces_pc_vpc['interface_type'], self.configured_interfaces_pc_vpc['interface_ports'], self.configured_interfaces_pc_vpc['interface_selector'], self.configured_interfaces_pc_vpc['interface_policy_group'])

        # create Attachable Access Entity profile
        createAttachableAccessEntityprofile.create_attachable_access_entity_profile(self.mo, self.attachable_entity_profile['name'], optional_args=self.attachable_entity_profile['optional_args'])
        self.commit_change()

        # create vCenter Domain
        self.check_if_mo_exist('uni/vmmp-' + self.vcenter_provider)
        vmm_domp = createVcenterDomain.create_vcenter_domain(self.mo, self.vcenter_domain, optional_args={'vlan': self.vlan['vlan_name'], 'vlan_mode': self.vlan['vlan_mode']})
        self.commit_change()

        # create Vcenter Credential and Controller
        createVcenterCredential.create_vcenter_credential(vmm_domp, self.vcenter_credential['profile'], self.vcenter_credential['vmm_user'], self.vcenter_credential['vmm_password'])
        vmm_ctrlrp = createVcenterController.create_vcenter_controller(vmm_domp, self.vcenter_controller['name'], self.vcenter_controller['host_or_ip'], self.vcenter_controller['data_center'], optional_args=self.vcenter_controller['optional_args'])
        vmm_usraccp_path = 'uni/vmmp-' + self.vcenter_provider + '/dom-' + self.vcenter_domain + '/usracc-' + self.vcenter_controller['optional_args']['associated_credential']
        createVcenterController.define_associated_credential(vmm_ctrlrp, vmm_usraccp_path)


if __name__ == '__main__':
    mo = LabCreatingAvCenterDomainProfile()