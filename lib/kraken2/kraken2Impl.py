# -*- coding: utf-8 -*-
#BEGIN_HEADER
import logging
import os
import subprocess
import pandas as pd
import shutil

from installed_clients.KBaseReportClient import KBaseReport
from installed_clients.ReadsUtilsClient import ReadsUtils
from installed_clients.AssemblyUtilClient import AssemblyUtil
from installed_clients.DataFileUtilClient import DataFileUtil
#END_HEADER


class kraken2:
    '''
    Module Name:
    kraken2

    Module Description:
    A KBase module: kraken2
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "0.0.1"
    GIT_URL = "git@github.com:mflynn-lanl/kbase-kraken2.git"
    GIT_COMMIT_HASH = "2993ea6b7451e8867881789e82f31252c504ea61"

    #BEGIN_CLASS_HEADER
    def _generate_DataTable(self, infile, outfile):
        f =  open(infile, "r")
        wf = open(outfile,"w")

        header = f.readline().strip()
        headerlist = [ x.strip() for x in header.split('\t')]

        wf.write("<head>\n")
        wf.write("<link rel='stylesheet' type='text/css' href='https://cdn.datatables.net/1.10.19/css/jquery.dataTables.css'>\n")
        wf.write("<script type='text/javascript' charset='utf8' src='https://code.jquery.com/jquery-3.3.1.js'></script>\n")
        wf.write("<script type='text/javascript' charset='utf8' src='https://cdn.datatables.net/1.10.19/js/jquery.dataTables.min.js'></script>\n")
        wf.write("</head>\n")
        wf.write("<body>\n")
        wf.write("""<script>
        $(document).ready(function() {
            $('#gottcha2_result_table').DataTable();
        } );
        </script>""")
        wf.write("<table id='gottcha2_result_table' class='display' style=''>\n")
        wf.write('<thead><tr>' + ''.join("<th>{0}</th>".format(t) for t in headerlist) + '</tr></thead>\n')
        wf.write("<tbody>\n")
        for line in f:
            if not line.strip():continue
            wf.write("<tr>\n")
            temp = [ x.strip() for x in line.split('\t')]
            wf.write(''.join("<td>{0}</td>".format(t) for t in temp))
            wf.write("</tr>\n")
        wf.write("</tbody>\n")
        wf.write("</table>")
        wf.write("</body>\n")

    def _generate_report_table(self, report_df, outfile, output_dir):
        pd.set_option('colheader_justify', 'center')  # FOR TABLE <th>
        with open(os.path.join(output_dir, 'df_style.css'), 'w') as fp:
            css_string = '''
            .mystyle {
                font-size: 11pt; 
                font-family: Arial;
                border-collapse: collapse; 
                border: 1px solid silver;
            
            }
            
            .mystyle td, th {
                padding: 5px;
            }
            
            .mystyle tr:nth-child(even) {
                background: #E0E0E0;
            }
            
            .mystyle tr:hover {
                background: silver;
                cursor: pointer;
            }
            '''
            fp.write(css_string)

        html_string = '''
        <html>
          <head>
          <link rel="stylesheet" type="text/css" href="df_style.css"/>
          <title>Kraken2 Report</title></head>
          <body>
            {table}
          </body>
        </html>.
        '''

        # OUTPUT AN HTML FILE
        with open(outfile, 'w') as f:
            f.write(html_string.format(table=report_df.to_html(classes='mystyle', index=False), css=os.path.join(output_dir, 'df_style.css')))

    def package_folder(self, folder_path, zip_file_name, zip_file_description):
        ''' Simple utility for packaging a folder and saving to shock '''
        if folder_path == self.shared_folder:
            raise ValueError ("cannot package scatch itself.  folder path: "+folder_path)
        elif not folder_path.startswith(self.shared_folder):
            raise ValueError ("cannot package folder that is not a subfolder of scratch.  folder path: "+folder_path)
        dfu = DataFileUtil(self.callback_url)
        if not os.path.exists(folder_path):
            raise ValueError ("cannot package folder that doesn't exist: "+folder_path)
        output = dfu.file_to_shock({'file_path': folder_path,
                                    'make_handle': 0,
                                    'pack': 'zip'})
        return {'shock_id': output['shock_id'],
                'name': zip_file_name,
                'label': zip_file_description}
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.shared_folder = config['scratch']
        logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                            level=logging.INFO)
        #END_CONSTRUCTOR
        pass


    def run_kraken2(self, ctx, params):
        """
        This example function accepts any number of parameters and returns results in a KBaseReport
        :param params: instance of mapping from String to unspecified object
        :returns: instance of type "ReportResults" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN run_kraken2

        # Download input data as FASTA or FASTQ
        logging.info('Calling run_kraken2')
        logging.info(f'params {params}')
        # Check for presence of input file types in params
        input_genomes = 'input_genomes' in params and len(params['input_genomes']) > 0 and None not in params['input_genomes']
        input_refs = 'input_refs' in params and len(params['input_refs']) > 0 and None not in params['input_refs']
        input_paired_refs = 'input_paired_refs' in params and len(params['input_paired_refs']) > 0  and None not in params['input_paired_refs']
        for name in ['workspace_name', 'db_type']:
            if name not in params:
                raise ValueError(
                    'Parameter "' + name + '" is required but missing')
        if not input_genomes and not input_refs and not input_paired_refs:
            raise ValueError(
                'You must enter either an input genome or input reads')

        if input_refs and input_paired_refs:
            raise ValueError(
                'You must enter either single-end or paired-end reads, '
                'but not both')

        if input_genomes and (input_refs or input_paired_refs):
            raise ValueError(
                'You must enter either an input genome or input reads, '
                'but not both')

        if input_genomes and (
                not isinstance(params['input_genomes'][0], str)):
            raise ValueError('Pass in a valid input genome string')

        if input_refs and (
                not isinstance(params['input_refs'], list)):
            raise ValueError('Pass in a list of input references')

        if input_paired_refs and (
                not isinstance(params['input_paired_refs'], list)):
            raise ValueError('Pass in a list of input references')

        logging.info(params['db_type'])
        logging.info(f'input_genomes {input_genomes} input_refs {input_refs} input_paired_refs {input_paired_refs}')
        input_string = []
        if input_genomes:
            assembly_util = AssemblyUtil(self.callback_url)
            fasta_file_obj = assembly_util.get_assembly_as_fasta(
                {'ref': params['input_genomes'][0]})
            logging.info(fasta_file_obj)
            fasta_file = fasta_file_obj['path']
            input_string.append(fasta_file)

        if input_refs:
            logging.info('Downloading Reads data as a Fastq file.')
            logging.info(f"input_refs {params['input_refs']}")
            readsUtil = ReadsUtils(self.callback_url)
            download_reads_output = readsUtil.download_reads(
                {'read_libraries': params['input_refs']})
            print(
                f"Input parameters {params['input_refs']}, {params['db_type']}"
                f"download_reads_output {download_reads_output}")
            fastq_files = []
            fastq_files_name = []
            for key, val in download_reads_output['files'].items():
                if 'fwd' in val['files'] and val['files']['fwd']:
                    fastq_files.append(val['files']['fwd'])
                    fastq_files_name.append(val['files']['fwd_name'])
                if 'rev' in val['files'] and val['files']['rev']:
                    fastq_files.append(val['files']['rev'])
                    fastq_files_name.append(val['files']['rev_name'])
            logging.info(f"fastq files {fastq_files}")
            input_string.append(' '.join(fastq_files))

        if input_paired_refs:
            logging.info('Downloading Reads data as a Fastq file.')
            logging.info(f"input_refs {params['input_paired_refs']}")
            readsUtil = ReadsUtils(self.callback_url)
            download_reads_output = readsUtil.download_reads(
                {'read_libraries': params['input_paired_refs']})
            print(
                f"Input parameters {params['input_paired_refs']}, {params['db_type']}"
                f"download_reads_output {download_reads_output}")
            fastq_files = []
            fastq_files_name = []
            # input_string.append('--paired')
            for key, val in download_reads_output['files'].items():
                if 'fwd' in val['files'] and val['files']['fwd']:
                    fastq_files.append(val['files']['fwd'])
                    fastq_files_name.append(val['files']['fwd_name'])
                if 'rev' in val['files'] and val['files']['rev']:
                    fastq_files.append(val['files']['rev'])
                    fastq_files_name.append(val['files']['rev_name'])
            # if len(fastq_files) % 2 != 0:
            #     raise ValueError('There must be an even number of Paired-end reads files')
            logging.info(f"fastq files {fastq_files}")
            input_string.extend(fastq_files)

        logging.info(f'input_string {input_string}')

        output_dir = os.path.join(self.shared_folder, 'kraken2_output')
        report_file_name = 'report.txt'
        report_file = os.path.join(output_dir, report_file_name)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        outprefix = "kraken2"

        cmd = ['/kb/module/lib/kraken2/src/kraken2.sh',
               '-d', '/data/kraken2/' + params['db_type'],
               '-o', output_dir, '-p', outprefix,
               '-t', '1', '-i']
        cmd.extend(input_string)

        # cmd = ['kraken2', '--db', '/data/kraken2/' + params['db_type'],
        #        '--output', output_dir, '--report', report_file,
        #        '--threads', '1']
        # cmd.extend(['--confidence', str(params['confidence'])]) if 'confidence' in params else cmd

        logging.info(f'cmd {cmd}')
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        logging.info(f'subprocess {p.communicate()}')


        summary_file = os.path.join(output_dir, outprefix + '.report.csv')
        report_dir = os.path.join(output_dir, 'html_report')
        if not os.path.exists(report_dir):
            os.makedirs(report_dir)
        summary_file_dt = os.path.join(report_dir, 'kraken2.datatable.html')
        self._generate_DataTable(summary_file, summary_file_dt)
        shutil.copy2('/kb/module/lib/kraken2/src/index.html', os.path.join(report_dir, 'index.html'))
        shutil.copy2(os.path.join(output_dir, outprefix + '.krona.html'),
                     os.path.join(report_dir, 'kraken2.krona.html'))
        shutil.move(os.path.join(output_dir, outprefix + '.tree.svg'), os.path.join(report_dir, 'kraken2.tree.svg'))
        html_zipped = self.package_folder(report_dir, 'index.html', 'index.html')

        # columns = [
        #     'Percentage of fragments covered by the clade rooted at this taxon',
        #     'Number of fragments covered by the clade rooted at this taxon',
        #     'Number of fragments assigned directly to this taxon', 'rank code',
        #     'taxid', 'name']
        # report_df = pd.read_csv(report_file, sep='\t',
        #                         header=None, names=columns)
        # code_dict = {'U': 'Unclassified', 'R': 'Root', 'D': 'Domain',
        #              'K': 'Kingdom', 'P': 'Phylum', 'C': 'Class', 'O': 'Order',
        #              'F': 'Family', 'G': 'Genus', 'S': 'Species'}
        # report_df['rank code'] = report_df['rank code'].apply(
        #     lambda x: code_dict[x[0]] + x[1] if len(x) > 1 else code_dict[x])


        # self._generate_report_table(report_df, report_html_file, output_dir)
        # report_df.to_html(report_html_file, classes='Kraken2_report', index=False)
        # html_zipped = self.package_folder(output_dir, 'report.html',
        #                                   'report')
        # Step 5 - Build a Report and return
        objects_created = []
        output_files = os.listdir(output_dir)
        output_files_list = []
        for output in output_files:
            if not os.path.isdir(output):
                output_files_list.append(
                    {'path': os.path.join(output_dir, output), 'name': output})
        message = f"Kraken2 run finished on {input_string} against {params['db_type']}."
        report_params = {'message': message,
                         'workspace_name': params.get('workspace_name'),
                         'objects_created': objects_created,
                         'file_links': output_files_list,
                         'html_links': [html_zipped],
                         'direct_html_link_index': 0,
                         'html_window_height': 460}

        # STEP 6: construct the output to send back
        kbase_report_client = KBaseReport(self.callback_url)
        report_output = kbase_report_client.create_extended_report(
            report_params)
        report_output['report_params'] = report_params
        logging.info(report_output)
        # Return references which will allow inline display of
        # the report in the Narrative
        output = {'report_name': report_output['name'],
                  'report_ref': report_output['ref'],
                  'report_params': report_output['report_params']
                  }
        #END run_kraken2

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method run_kraken2 return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
