from aiogram.utils.helper import Helper, HelperMode, ListItem, Item


# Следить за количеством СТЕЙТОВ ИНАЧЕ БУДЕТ ЕБАТЬ МОЗГИ!
class TestStates(Helper):
    mode = HelperMode.snake_case

    TEST_STATE_0 = ListItem()
    TEST_STATE_1 = ListItem()
    TEST_STATE_2 = ListItem()
    TEST_STATE_3 = ListItem()
    TEST_STATE_4 = ListItem()
    TEST_STATE_5 = ListItem()
    TEST_STATE_6 = ListItem()
    TEST_STATE_7 = ListItem()
    TEST_STATE_8 = ListItem()
    TEST_STATE_9 = ListItem()


if __name__ == '__main__':
    print(TestStates.all())
