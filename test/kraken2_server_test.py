# -*- coding: utf-8 -*-
import os
import time
import unittest
from configparser import ConfigParser
import subprocess
import logging
from pprint import pprint

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
    def getWsClient(self):
        return self.__class__.wsClient
    # NOTE: According to Python unittest naming rules test method names
    # should start from 'test'. # noqa
    def test_param(self):
        print('test_param')
        # Prepare test objects in workspace if needed using
        # self.getWsClient().save_objects({'workspace': self.getWsName(),
        #                                  'objects': []})
        #
        # Run your method by
        # ret = self.getImpl().your_method(self.getContext(), parameters...)
        #
        # Check returned data with
        # self.assertEqual(ret[...], ...) or other unittest methods
        # input_genomes = ["79/16/1"]
        input_refs = ['22956/5/2']
        test_fastq_reads = ['22956/22/1'] # test.fastq_reads
        two_reads_set = ['22956/25/1'] #two_se_reads_set (v1) test.fastq_reads (v1) rhodo.art.q50.SE.reads.fastq (v2)
        test_reads_set = ['22956/23/1'] # reads set with single read (test_reads_set)
        input_paired_refs = ['22956/8/1', '22956/7/1']
        print(f"input_refs {input_refs}")
    #
    #     # Test that either input_genomes or reads
    #     with self.assertRaises(ValueError):
    #         self.serviceImpl.run_kraken2(self.ctx,
    #                                        {'workspace_name': self.wsName,
    #                                         'input_genomes': [],
    #                                         'input_refs': [],
    #                                         'input_paired_refs': [None],
    #                                         'db_type': 'minikraken2_v1_8GB'
    #                                         })
    #     with self.assertRaises(ValueError):
    #         ret = self.serviceImpl.run_kraken2(self.ctx,
    #                                        {'workspace_name': self.wsName,
    #                                         'input_genomes': input_genomes,
    #                                         'input_refs': input_refs,
    #                                         'input_paired_refs': [],
    #                                         'db_type': 'minikraken2_v1_8GB'
    #                                         })
    #         print(f'ret {ret[0]}')
    #
    #     with self.assertRaises(ValueError):
    #         ret = self.serviceImpl.run_kraken2(self.ctx,
    #                                        {'workspace_name': self.wsName,
    #                                         'input_genomes': [],
    #                                         'input_refs': input_refs,
    #                                         'input_paired_refs':
    #                                             input_paired_refs,
    #                                         'db_type': 'minikraken2_v1_8GB'
    #                                         })
    #
    #
        # Test with single-ended reads
        # result = self.serviceImpl.run_kraken2(self.ctx,
        #                                    {'workspace_name': self.wsName,
        #                                     'input_refs': refs,
        #                                     'db_type': 'minikraken2_v1_8GB'})[0]
        # logging.info(f"report_ref {result}")
        # logging.info(f"report_ref {result['report_ref']}")
        # self.assertIn('report_name', result)
        # self.assertIn('report_ref', result)
        # report = self.getWsClient().get_objects2({'objects': [{'ref': result['report_ref']}]})['data'][0]['data']
        # logging.info(f'print report {report}')
        # pprint(report)
        # self.assertIn('direct_html', report)
        # self.assertIn('file_links', report)
        # self.assertIn('html_links', report)
        # self.assertIn('objects_created', report)
        # self.assertIn('text_message', report)

        result = self.serviceImpl.run_kraken2(self.ctx,
                                           {'workspace_name': self.wsName,
                                            'input_refs': two_reads_set,
                                            'confidence': 0.1,
                                            'db_type': 'minikraken2_v1_8GB'})[0]

        logging.info(f"report_ref {result}")
        logging.info(f"report_ref {result['report_ref']}")
        self.assertIn('report_name', result)
        self.assertIn('report_ref', result)
        report = self.getWsClient().get_objects2({'objects': [{'ref': result['report_ref']}]})['data'][0]['data']
        logging.info(f'print report {report}')
        pprint(report)
        self.assertIn('direct_html', report)
        self.assertIn('file_links', report)
        self.assertIn('html_links', report)
        self.assertIn('objects_created', report)
        self.assertIn('text_message', report)


    # def test_kraken2(self):
    #     print('test_kraken2')
    #     self.assertTrue(
    #         os.path.exists('/data/kraken2/16S_Greengenes_20190418'))
    #     self.assertTrue(os.path.exists(
    #         '/data/kraken2/minikraken2_v1_8GB/database100mers.kmer_distrib'))

        # Test fasta input with kraken-microbial database -- much larger db and
        # takes a long time to run
        # cmd = ['kraken2', '-db', '/data/kraken2/kraken-microbial',
        #        '--report', 'test_fasta.txt', '--threads', '1',
        #        '/data/kraken2/test.fasta']
        # logging.info(f'cmd {cmd}')
        # p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
        #                      stderr=subprocess.STDOUT)
        # logging.info(p.communicate())
        #
        # self.assertTrue(os.path.exists('test_fasta.txt'))
        # logging.info(f'current directory {os.getcwd()}')
        # with open('test_fasta.txt', 'r') as fp:
        #     logging.info('print summary')
        #     lines = fp.readlines()
        #     # for line in lines:
        #     #     logging.info(line.split('\t')[-1].strip())
        # self.assertEqual(lines[-1].split('\t')[-1].strip(),
        # 'Zaire ebolavirus')

        # Test fasta input with minikraken2 db
        # cmd = ['kraken2', '-db', '/data/kraken2/minikraken2_v1_8GB',
        #        '--report', 'test_fasta.txt', '--threads', '1',
        #        '/data/kraken2/test.fasta']
        # output_dir = '/kb/module/work/output'
        # output_csv = os.path.join(output_dir, 'kraken2.report.csv')
        # cmd = ['/kb/module/lib/kraken2/src/kraken2.sh',
        #        '-d', '/data/kraken2/minikraken2_v1_8GB',
        #        '-o', output_dir,'-t','1','-p', 'kraken2',
        #        '-i', '/data/kraken2/test.fasta']
        #
        # logging.info(f'cmd {cmd}')
        # p = subprocess.Popen(' '.join(cmd), stdout=subprocess.PIPE,
        #                      stderr=subprocess.STDOUT, shell=True)
        # logging.info(p.communicate())
        #
        # self.assertTrue(os.path.exists(output_csv))
        # logging.info(f'current directory {os.getcwd()}')
        # with open(output_csv, 'r') as fp:
        #     logging.info('print summary')
        #     lines = fp.readlines()
        #     # for line in lines:
        #     #     logging.info(line.split('\t')[-1].strip())
        # self.assertEqual(lines[-1].split('\t')[-1].strip(), 'Zaire ebolavirus')
        # #
        # # # Test fastq input
        # # cmd = ['kraken2', '-db', '/data/kraken2/minikraken2_v1_8GB',
        # #        '--report', 'test_fastq.txt', '--threads', '1', '--fastq-input',
        # #        '/data/kraken2/test.fastq']
        # cmd = ['/kb/module/lib/kraken2/src/kraken2.sh',
        #        '-d', '/data/kraken2/minikraken2_v1_8GB',
        #        '-o', output_dir, '-t', '1', '-p', 'kraken2',
        #        '-i', '/data/kraken2/test.fastq']
        # logging.info(f'cmd {cmd}')
        # p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
        #                      stderr=subprocess.STDOUT, shell=True)
        # logging.info(p.communicate())
        #
        # self.assertTrue(os.path.exists(output_csv))
        # logging.info(f'current directory {os.getcwd()}')
        # with open(output_csv, 'r') as fp:
        #     logging.info('print summary')
        #     lines = fp.readlines()
        #     for line in lines:
        #         logging.info(line.split('\t')[-1].strip())
        # if len(line.split('\t')) == 0:
        #     self.assertEqual(lines[-1].strip(),
        #                      'Zaire ebolavirus')
        # else:
        #     self.assertEqual(lines[-1].split('\t')[-1].strip(), 'Zaire ebolavirus')
