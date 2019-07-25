
from hugme.__key__ import acc, key
from datetime import datetime
from hugme import HugMe


class FileManager(HugMe):
    def __init__(self):
        super(FileManager, self).__init__()

    def get_files_from_dir(self, directory):
        from os import listdir
        return listdir(directory)

    def concatenate_files(self):
        """ Consolida a base de reclamações de todas as empresas em apenas um arquivo """
        from pandas import read_excel, DataFrame
        from datetime import datetime

        print('\n' + datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'Concatenando os arquivos ...')

        base_reclamacoes = DataFrame()
        for empresa, file in self.downloaded_files.items():
            df = read_excel(self.destination_folder + file, header=3)
            df['Empresa'] = empresa
            base_reclamacoes = base_reclamacoes.append(df)

        for col in base_reclamacoes.columns:
            if 'Unnamed' in col:
                base_reclamacoes.drop(columns=col, inplace=True)

        self.final_file = self.destination_folder + datetime.now().strftime('%Y%m%d%H%M%S') + '_base_reclamacoes.csv'
        base_reclamacoes.to_csv(self.final_file, index=False)

    def delete_all_downloaded_files(self):
        """ Deleta os arquivos baixados """
        from os import remove

        for file in list(self.downloaded_files.values()):
            remove(self.destination_folder + file)


class StorageAccount(HugMe):
    def __init__(self, local_file=None, move_to='blob'):
        super(StorageAccount, self).__init__()
        self.local_file = self.final_file if local_file is None else local_file
        self.move_to = move_to

        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = 'Movendo arquivo final para o {} storage...'.format(move_to)
        print(time, message)

    def blob(self, container, blob):
        from azure.storage.blob import BlockBlobService, PublicAccess

        block_blob_service = BlockBlobService(account_name=acc, account_key=key)
        block_blob_service.set_container_acl('final', public_access=PublicAccess.Container)
        block_blob_service.create_blob_from_path(
            container_name=container,
            blob_name=blob,
            file_path=self.local_file,
        )

    def files(self, share, directory, file):
        from azure.storage.file import FileService

        file_service = FileService(account_name=acc, account_key=key)
        file_service.create_file_from_path(
            share_name=share,
            directory_name=directory,
            file_name=file,
            local_file_path=self.local_file,
        )


if __name__ == '__main__':
    pass

