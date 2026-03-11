from datetime import datetime


class Rules:
    @staticmethod
    def boolean(arg: str) -> bool:
        """
        A boolean is a string that can be either "true" or "false".
        """
        return arg.lower() in ["true", "false"]

    @staticmethod
    def integer(arg: str | int) -> bool:
        """
        An integer is a string that can only contain digits. It must be positive.
        """
        try:
            return str(arg).isdigit()
        except Exception:
            return False

    @staticmethod
    def float(arg: str | int) -> bool:
        """
        A float is a string that can only contain digits and a decimal point. It must be positive.
        """
        try:
            return float(arg) >= 0
        except ValueError:
            return False

    @staticmethod
    def timestamp_ms(arg: str | int) -> bool:
        """
        A timestamp in milliseconds is a string that can only contain digits. It must be 13 characters long.
        """
        return all([x in "0123456789" for x in str(arg)]) and len(str(arg)) == 13

    @staticmethod
    def timestamp_s(arg: str | int) -> bool:
        """
        A timestamp in seconds is a string that can only contain digits. It must be 10 characters long.
        """
        return all([x in "0123456789" for x in str(arg)]) and len(str(arg)) == 10

    @staticmethod
    def timestamp(arg: str) -> bool:
        """
        A timestamp can be in milliseconds (13 characters) or seconds (10 characters) format.
        """
        return Rules.timestamp_ms(arg) or Rules.timestamp_s(arg)

    @staticmethod
    def history(arg: str | int) -> bool:
        """
        A history is a string that can only contain digits. It must be between 1 and 365.
        """
        return Rules.integer(arg) and 1 <= int(arg) <= 365

    @staticmethod
    def date(arg: str) -> bool:
        """
        A date is a string in the DD-MM-YYYY format.
        """
        try:
            datetime.strptime(arg, "%d-%m-%Y")
            return True
        except ValueError:
            return False
