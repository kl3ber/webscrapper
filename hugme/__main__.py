
from hugme import HugMe
from datetime import datetime
from time import sleep, time


def main(operacao):
    temp_ini = datetime.now().replace(microsecond=0)

    with HugMe(operacao=operacao) as rpa:
        """ Login e navegação """
        # rpa.start_driver()
        rpa.access_website()
        rpa.login()
        if not rpa.logged:
            return

        rpa.access_reports_page()
        rpa.select_preset_filter()

        """ Gerar relatórios para todas as empresas """
        for empresa, selection_name in rpa.empresas.items():
            rpa.select_empresa(empresa=selection_name)
            titulo = empresa.replace(' ', '_') + '_' + str(time()).replace('.', '')
            rpa.submit_report(report_name=titulo)
            rpa.new_reports[empresa] = titulo

        to_be_downloaded = list(rpa.new_reports.values())
        print('\nVerificando disponibilidade de download...\n')

        """ Verificar se o relatório foi gerado e fazer o download """
        while not to_be_downloaded == []:
            rpa.driver.refresh()
            rpa.scrolldown_load_older_reports(times=2)
            # rpa.load_more_reports(times=5)
            sleep(10)

            for report in to_be_downloaded:
                index, download = rpa.find_report(report_name=report)
                if download:
                    rpa.download_report(index)
                    while not rpa.check_file_download(report): pass
                    sleep(5)

                    rpa.delete_report(index)
                    to_be_downloaded.remove(report)
                    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'Download: ', report)
            sleep(20)

    """ Concatenar os arquivos baixados e gerar a base consolidada """
    rpa.get_downloaded_files_names()
    rpa.concatenate_files()
    rpa.delete_all_downloaded_files()
    rpa.move_to_blob()

    print('\nExtração concluída.')
    print('\nTempo de execução: ', datetime.now().replace(microsecond=0) - temp_ini)


def schedule_run():
    import schedule

    schedule.every().day.at("08:00").do(main, operacao='via_varejo')
    schedule.every().day.at("14:00").do(main, operacao='via_varejo')
    schedule.every().day.at("18:00").do(main, operacao='via_varejo')

    schedule.every().day.at("08:00").do(main, operacao='pao_de_acucar')

    schedule.every().day.at("08:00").do(main, operacao='first_data')

    while True:
        schedule.run_pending()
        sleep(60)


if __name__ == '__main__':
    schedule_run()


