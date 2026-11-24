from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    bot_token: str
    webhook_secret: str
    webhook_base_url: str
    database_url: str
    admin_ids: str = ""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    @property
    def admins(self):
        return {int(x.strip()) for x in self.admin_ids.split(",") if x.strip()}
settings = Settings()
