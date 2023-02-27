from decimal import localcontext, Decimal, ROUND_DOWN, ROUND_UP


class DecimalTool:
    """
    精度小數點第五位,無條件捨去

    目標需求 報表金額 計算至 小數第二 位
    目標需求 顯示金額 計算至 整數 位
    """

    _DEFAULT_ROUNDING = ROUND_DOWN

    _ACCURATE_DIGIT = 5

    ZERO = Decimal('0.0')
    NEGATIVE_ONE = Decimal('-1')

    @staticmethod
    def to_decimal(num):
        """
        單 轉換 decimal

        >>> DecimalTool.to_decimal('0.1')
        Decimal('0.1')
        >>> DecimalTool.to_decimal(0.1)
        Decimal('0.1')
        >>> DecimalTool.to_decimal(Decimal('0.1'))
        Decimal('0.1')
        """
        return num if isinstance(num, Decimal) else Decimal(str(num))

    @classmethod
    def convert_numbers(cls, nums):
        """
        多 轉換 decimal
        """
        return [cls.to_decimal(_) for _ in nums]

    @classmethod
    def rounding_down(cls, num, digit, is_format=True):
        with localcontext() as ctx:
            ctx.rounding = ROUND_DOWN
            place = cls.to_decimal(10) ** -digit
            result = cls.to_decimal(num).quantize(place)
            return f'{result:.{digit}f}' if is_format else result

    @classmethod
    def rounding_up(cls, num, digit, is_format=True):
        with localcontext() as ctx:
            ctx.rounding = ROUND_UP
            place = cls.to_decimal(10) ** -digit
            result = cls.to_decimal(num).quantize(place)
            return f'{result:.{digit}f}' if is_format else result

    @classmethod
    def sum(cls, nums, digit=None, rounding=None):
        nums = cls.convert_numbers(nums=nums)
        with localcontext() as ctx:
            ctx.prec = digit or cls._ACCURATE_DIGIT
            ctx.rounding = rounding or cls._DEFAULT_ROUNDING
            return sum(nums)

    @classmethod
    def diff(cls, a, b, digit=None, rounding=None):
        num_a = cls.to_decimal(num=a)
        num_b = cls.to_decimal(num=b)
        with localcontext() as ctx:
            ctx.prec = digit or cls._ACCURATE_DIGIT
            ctx.rounding = rounding or cls._DEFAULT_ROUNDING
            return num_a - num_b

    @classmethod
    def invert(cls, num, digit=None, rounding=None):
        num = cls.to_decimal(num=num)
        with localcontext() as ctx:
            ctx.prec = digit or cls._ACCURATE_DIGIT
            ctx.rounding = rounding or cls._DEFAULT_ROUNDING
            return num * cls.NEGATIVE_ONE
