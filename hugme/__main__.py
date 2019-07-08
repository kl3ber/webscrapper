
import schedule


def extract_reports_from_portal():
    from time import time, sleep
    from datetime import datetime
    from hugme import HugMe

    temp_ini = datetime.now().replace(microsecond=0)

    rpa = HugMe()
    rpa.login()
    if not rpa.logged:
        rpa.driver.quit()
        return

    rpa.access_reports_page()
    rpa.select_preset_filter()

    # Gerar relatórios para todas as empresas
    for empresa, selection_name in rpa.empresas.items():
        rpa.select_empresa(empresa=selection_name)
        titulo = empresa.replace(' ', '_') + '_' + str(time()).replace('.', '')
        rpa.submit_report(report_name=titulo)
        rpa.new_reports[empresa] = titulo

    to_be_downloaded = list(rpa.new_reports.values())
    print('\nVerificando disponibilidade de download...\n')

    # Verificar se o relatório foi gerado e fazer o download
    while not to_be_downloaded == []:
        rpa.driver.refresh()
        while 'Carregar mais' not in rpa.driver.page_source: pass
        sleep(3)
        rpa.scrolldown_load_older_reports(times=5)
        sleep(10)

        for report in to_be_downloaded:
            index, download = rpa.find_report(report_name=report)
            if download:
                rpa.download_report(index)
                while not rpa.check_file_download(report): pass
                sleep(5)

                rpa.delete_report(index)
                rpa.move_downloaded_file(report)
                to_be_downloaded.remove(report)
                print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'Download: ', report)
        sleep(20)

    rpa.driver.close()
    rpa.driver.quit()
    sleep(3)

    # Concatenar os arquivos baixados e gerar a base consolidada
    rpa.downloaded_files = rpa.get_downloaded_files_names()
    rpa.move_all_downloaded_files()
    rpa.concatenate_files()
    rpa.delete_all_downloaded_files()
    rpa.move_to_storage_account()

    print('\nExtração concluída.\n')

    print('Tempo de execução: ', datetime.now().replace(microsecond=0) - temp_ini)


def schedule_run():
    # schedule.every().day.at("17:80").do(extract_reports_from_portal)
    # schedule.every(2).hours.do(extract_reports_from_portal)

    schedule.every().day.at("08:00").do(extract_reports_from_portal)
    schedule.every().day.at("11:00").do(extract_reports_from_portal)
    schedule.every().day.at("16:00").do(extract_reports_from_portal)

    while True:
        schedule.run_pending()
        sleep(60)


if __name__ == '__main__':
    from datetime import datetime
    from time import sleep

    schedule_run()





