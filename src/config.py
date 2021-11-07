from dotenv import dotenv_values

class Config:
    EXPORT_FILE_NAME= ''
    BATHC=9
    def __init__(self) -> None:
        env = dotenv_values('.env')
        self.EXPORT_FILE_NAME = env['EXPORT_FILE_NAME']
        self.BATHC  = int(env['BATCH'])
