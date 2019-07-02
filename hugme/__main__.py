
def extract_reports_from_portal():
    from time import time, sleep
    from datetime import datetime
    from hugme import HugMe

    rpa = HugMe()
    rpa = rpa.access_website()
    rpa.login()
    rpa.access_reports_page()
    rpa.select_preset_filter()

    # Gerar relatórios para todas as empresas
    for empresa, selection_name in rpa.empresas.items():
        rpa.select_empresa(empresa=selection_name)
        titulo = empresa.replace(' ', '_') + '_' + str(time()).replace('.', '')
        rpa.submit_report(report_name=titulo)
        rpa.new_reports.append(titulo)

    to_be_downloaded = rpa.new_reports.copy()
    print('\nVerificando disponibilidade de download...\n')

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
                # rpa.move_downloaded_file(report)
                to_be_downloaded.remove(report)
                print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'Download: ', report)
        sleep(20)

    rpa.driver.close()
    rpa.driver.quit()

    sleep(3)
    rpa.downloaded_files = rpa.move_all_downloaded_files()

    print('\nExtração concluída.\n')


if __name__ == '__main__':
    from datetime import datetime

    temp_ini = datetime.now().replace(microsecond=0)
    extract_reports_from_portal()
    print('Tempo de execução: ', datetime.now().replace(microsecond=0) - temp_ini)

