from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_user: str = "oncall"
    db_pass: str = "oncall"
    db_name: str = "oncall"
    db_host: str = "localhost"
    db_port: int = 5432
    clicksend_username: str = ""
    clicksend_api_key: str = ""
    clicksend_from_number: str = ""  # optional: leave blank to let ClickSend pick a sender

    dry_run: bool = True

    # Comma-separated, matched up by position, e.g.:
    # SURGEON_NAMES="Dr A,Dr B,Dr C"
    # SURGEON_NUMBERS="+6421111111,+6421222222,+6421333333"
    surgeon_names: str = ""
    surgeon_numbers: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.db_user}:{self.db_pass}@{self.db_host}:{self.db_port}/{self.db_name}"


settings = Settings()
