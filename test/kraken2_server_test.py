# -*- coding: utf-8 -*-
import os
import time
import unittest
from configparser import ConfigParser
import subprocess
import logging

from kraken2.kraken2Impl import kraken2
from kraken2.kraken2Server import MethodContext
from kraken2.authclient import KBaseAuth as _KBaseAuth

from installed_clients.WorkspaceClient import Workspace
from installed_clients.AssemblyUtilClient import AssemblyUtil


class kraken2Test(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = os.environ.get('KB_AUTH_TOKEN', None)
        config_file = os.environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('kraken2'):
            cls.cfg[nameval[0]] = nameval[1]
        # Getting username from Auth profile for token
        authServiceUrl = cls.cfg['auth-service-url']
        auth_client = _KBaseAuth(authServiceUrl)
        user_id = auth_client.get_user(token)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': token,
                        'user_id': user_id,
                        'provenance': [
                            {'service': 'kraken2',
                             'method': 'please_never_use_it_in_production',
                             'method_params': []
                             }],
                        'authenticated': 1})
        cls.wsURL = cls.cfg['workspace-url']
        cls.wsClient = Workspace(cls.wsURL)
        cls.serviceImpl = kraken2(cls.cfg)
        cls.scratch = cls.cfg['scratch']
        cls.callback_url = os.environ['SDK_CALLBACK_URL']
        suffix = int(time.time() * 1000)
        cls.wsName = "test_Kraken2_" + str(suffix)
        ret = cls.wsClient.create_workspace({'workspace': cls.wsName})  # noqa

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')

    # NOTE: According to Python unittest naming rules test method names should start from 'test'. # noqa
    def test_param(self):
        # Prepare test objects in workspace if needed using
        # self.getWsClient().save_objects({'workspace': self.getWsName(),
        #                                  'objects': []})
        #
        # Run your method by
        # ret = self.getImpl().your_method(self.getContext(), parameters...)
        #
        # Check returned data with
        # self.assertEqual(ret[...], ...) or other unittest methods
        input_genomes = "79/16/1"
        input_refs = ['22956/5/2']
        input_paired_refs = ['22956/8/1', '22956/7/1']
        print(f"input_refs {input_refs}")

        # Test that either input_genomes or reads
        with self.assertRaises(ValueError):
            self.serviceImpl.run_kraken2(self.ctx,
                                           {'workspace_name': self.wsName,
                                            'input_genomes': None,
                                            'db_type': 'minikraken2_v1_8GB'
                                            })
        with self.assertRaises(ValueError):
            ret = self.serviceImpl.run_kraken2(self.ctx,
                                           {'workspace_name': self.wsName,
                                            'input_genomes': input_genomes,
                                            'input_refs': input_refs,
                                            'db_type': 'minikraken2_v1_8GB'
                                            })
            print(f'ret {ret[0]}')

        with self.assertRaises(ValueError):
            ret = self.serviceImpl.run_kraken2(self.ctx,
                                           {'workspace_name': self.wsName,
                                            'input_refs': input_refs,
                                            'input_paired_refs': input_paired_refs,
                                            'db_type': 'minikraken2_v1_8GB'
                                            })
            print(f'ret {ret[0]}')

        # Test with single-ended reads
        ret = self.serviceImpl.run_kraken2(self.ctx,
                                           {'workspace_name': self.wsName,
                                            'input_refs': input_refs,
                                            'db_type': 'minikraken2_v1_8GB'})
        self.assertTrue('report_name' in ret[0].keys())
        self.assertTrue('report_ref' in ret[0].keys())
        self.assertTrue('report_params' in ret[0].keys())
        self.assertEqual('kraken2_output.zip',
                         ret[0]['report_params']['file_links'][0]['name'])
        self.assertIn('test_Kraken2_',
                      ret[0]['report_params']['workspace_name'])
        self.assertIn('minikraken2_v1_8GB', ret[0]['report_params']['message'])

        # Test with paired single-end reads
        ret = self.serviceImpl.run_kraken2(self.ctx,
                                           {'workspace_name': self.wsName,
                                            'input_paired_refs':
                                                input_paired_refs,
                                            'db_type': 'minikraken2_v1_8GB'})
        self.assertTrue('report_name' in ret[0].keys())
        self.assertTrue('report_ref' in ret[0].keys())
        self.assertTrue('report_params' in ret[0].keys())
        self.assertEqual('kraken2_output.zip',
                         ret[0]['report_params']['file_links'][0]['name'])
        self.assertIn('test_Kraken2_', ret[0]['report_params']['workspace_name'])
        self.assertIn('minikraken2_v1_8GB', ret[0]['report_params']['message'])
        print(f'ret {ret[0]}')

        # Test with Assemblies
        ret = self.serviceImpl.run_kraken2(self.ctx,
                                           {'workspace_name': self.wsName,
                                            'input_genomes': input_genomes,
                                            'db_type': 'minikraken2_v1_8GB'})

        print("report", ret[0])
        self.assertTrue('report_name' in ret[0].keys())
        self.assertTrue('report_ref' in ret[0].keys())
        self.assertTrue('report_params' in ret[0].keys())
        self.assertEqual('kraken2_output.zip',
                         ret[0]['report_params']['file_links'][0]['name'])
        self.assertIn('test_Kraken2_', ret[0]['report_params']['workspace_name'])
        self.assertIn('Shewanella_oneidensis_MR-1_assembly.fa', ret[0]['report_params']['message'])
        self.assertIn('minikraken2_v1_8GB', ret[0]['report_params']['message'])


    def test_kraken2(self):
        self.assertTrue(os.path.exists('/data/kraken2/16S_Greengenes_20190418'))
        self.assertTrue(os.path.exists(
            '/data/kraken2/minikraken2_v1_8GB/database100mers.kmer_distrib'))

        # Test fasta input
        cmd = ['kraken2', '-db', '/data/kraken2/minikraken2_v1_8GB',
               '--report', 'test_fasta.txt', '--threads', '1', '--fasta-input', '/data/kraken2/test.fasta']
        logging.info(f'cmd {cmd}')
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        logging.info(p.communicate())

        self.assertTrue(os.path.exists('test_fasta.txt'))
        logging.info(f'current directory {os.getcwd()}')
        with open('test_fasta.txt', 'r') as fp:
            logging.info('print summary')
            lines = fp.readlines()
            # for line in lines:
            #     logging.info(line.split('\t')[-1].strip())
        self.assertEqual(lines[-1].split('\t')[-1].strip(), 'Zaire ebolavirus')

        # Test fastq input
        cmd = ['kraken2', '-db', '/data/kraken2/minikraken2_v1_8GB',
               '--report', 'test_fastq.txt', '--threads', '1', '--fastq-input',
               '/data/kraken2/test.fastq']
        logging.info(f'cmd {cmd}')
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        logging.info(p.communicate())

        self.assertTrue(os.path.exists('test_fastq.txt'))
        logging.info(f'current directory {os.getcwd()}')
        with open('test_fastq.txt', 'r') as fp:
            logging.info('print summary')
            lines = fp.readlines()
            for line in lines:
                logging.info(line.split('\t')[-1].strip())
        self.assertEqual(lines[-1].split('\t')[-1].strip(), 'Borrelia miyamotoi')