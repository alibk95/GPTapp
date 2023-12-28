from beverage_assistant import BeverageAssistant
import pytest


@pytest.fixture
def order_input(request):
    return request.param

class TestBeverageAssistant():
    
    @pytest.mark.repeat(1)
    @pytest.mark.parametrize("order_input", [
        "a single shot espresso with milk please",
        "I would like a single shot espresso with a little milk",
        "Give me an espresso with some milk",
        "I'll take a single shot espresso, add a bit of milk",
        "Can I get a single shot espresso with milk?"
    ], indirect=True)
    def test_single_shot_espresso_with_milk(self, order_input):
        assistant = BeverageAssistant()
        order_list = assistant.run_order(order_input)
        order_list = order_list[0]

        if "single shot" in order_list[0]:
            order_list[0] = order_list[0].replace("single shot", "single")

        expected_output = ['{"name": "espresso", "category": "hot drinks", "sizes": "single", "extras": "milk"}']
        
        assistant = None

        print("output      : ", order_list)
        print("expected_out: ", expected_output)
        assert order_list == expected_output
    
    @pytest.mark.repeat(1)
    @pytest.mark.parametrize("order_input", [
        "an espresso please",
    ], indirect=True)
    def test_add_item_with_missing_info(self, order_input):
        assistant = BeverageAssistant()
        response = assistant.run_order(order_input)
        
        reply = assistant.run_order("single shot with milk please")
        reply = reply[0]
        
        expected_output = ['{"name": "espresso", "category": "hot drinks", "sizes": "single shot", "extras": "milk"}']
        
        assistant = None

        print("output      : ", reply)
        print("expected_out: ", expected_output)
        assert reply == expected_output

    @pytest.mark.repeat(1)
    @pytest.mark.parametrize("order_input", [
        "a single shot espresso with sugar please",
        "I'd like a single shot espresso with sugar, please",
        "Please add sugar to my single espresso",
        "I want a single shot espresso, make it sweet with sugar",
        "Can you sweeten my single shot espresso with sugar?"
    ], indirect=True)    
    def test_single_shot_espresso_with_sugar(self, order_input):
        assistant = BeverageAssistant()
        order_list = assistant.run_order(order_input)
        order_list = order_list[0]

        if "single shot" in order_list[0]:
            order_list[0] = order_list[0].replace("single shot", "single")

        expected_output = ['{"name": "espresso", "category": "hot drinks", "sizes": "single", "extras": "sugar"}']
        
        assistant = None

        print("output      : ", order_list)
        print("expected_out: ", expected_output)
        assert order_list == expected_output

    @pytest.mark.repeat(1)
    @pytest.mark.parametrize("order_input", [
        "I would like to get an single shot espresso please",
        "Can I have a single shot espresso?",
        "Give me a single shot espresso",
        "I'll take a single shot espresso, please",
        "I want a single shot espresso"
    ], indirect=True)
    def test_single_shot_espresso_no_other_info(self, order_input):
        # if no info is given about the extras: the order_list at this stage 
        # should be still empty and the assistant is asking further questions.
        assistant = BeverageAssistant()
        order_list = assistant.run_order(order_input)
        order_list = order_list[0]

        expected_output = []
        
        assistant = None

        print("output      : ", order_list)
        print("expected_out: ", expected_output)
        assert order_list == expected_output

    @pytest.mark.repeat(1)
    @pytest.mark.parametrize("order_input", [
        "I would like to get a milkshake please",
        "Milkshake, please!",
        "I want a milkshake",
        "Give me a milkshake",
        "Can I get a milkshake?"
    ], indirect=True)
    def test_not_available_item(self, order_input):
        # Milkshake is not available in the product list
        assistant = BeverageAssistant()
        order_list = assistant.run_order(order_input)
        order_list = order_list[0]

        expected_output = []
        
        assistant = None

        print("output      : ", order_list)
        print("expected_out: ", expected_output)
        assert order_list == expected_output

    @pytest.mark.repeat(1)
    @pytest.mark.parametrize("order_input", [
        "a single shot espresso please",
        "Give me a single shot espresso",
        "I'd like a single shot espresso",
        "Can I get a single shot espresso?",
        "I want a single shot espresso"
    ], indirect=True)
    def test_add_item_function_call(self, order_input):
        # add_item
        assistant = BeverageAssistant()
        reply = assistant.run_order(order_input)
        
        assistant = None

        print("reply from assistant: ", reply)
        assert reply[1].function_call.name == "add_item"

    
    @pytest.mark.repeat(1)
    @pytest.mark.parametrize("order_input", [
        "I changed my mind. please remove the espresso",
        "Remove the espresso from my order, please",
        "Take the espresso off my order",
        "I don't want the espresso anymore. Remove it.",
        "Cancel the espresso in my order"
    ], indirect=True)
    def test_remove_item_function_call(self, order_input):
        # remove_item
        assistant = BeverageAssistant()
        reply = assistant.run_order(order_input)
        
        assistant = None

        print("reply from assistant: ", reply)
        assert reply[1].function_call.name == "remove_item"

    @pytest.mark.repeat(1)
    @pytest.mark.parametrize("order_input", [
        "I think I don't want anything anymore! ciao!",
        "Cancel my order. Goodbye!",
        "I changed my mind. No more drinks for me. Bye.",
        "I'm not in the mood for coffee anymore. Cancel my order.",
        "Sorry, cancel the order. I've changed my mind."
    ], indirect=True)
    def test_cancel_order_function_call(self, order_input):
        # cancel_order
        assistant = BeverageAssistant()
        reply = assistant.run_order(order_input)
        
        assistant = None
        
        print("reply from assistant: ", reply)
        assert reply[1].function_call.name == "cancel_order"

    @pytest.mark.repeat(1)
    @pytest.mark.parametrize("order_input", [
        "I think that's it. please go ahead with my order",
        "Ready to submit my order now",
        "I'm done with my order. Please proceed.",
        "Go ahead and submit my order",
        "Please submit my order now."
    ], indirect=True)
    def test_submit_order_function_call(self, order_input):
        # submit_order
        assistant = BeverageAssistant()
        reply = assistant.run_order(order_input)
        
        assistant = None

        print("reply from assistant: ", reply)
        assert reply[1].function_call.name == "submit_order"


    @pytest.mark.repeat(1)
    @pytest.mark.parametrize("order_input", [
        "a single shot espresso with milk please!",
    ], indirect=True)
    def test_add_item_and_submit_order(self, order_input):
        assistant = BeverageAssistant()
        response = assistant.run_order(order_input)
        
        reply = assistant.run_order("that's it thx.")
        reply = reply[0]
        
        expected_output = ['{"name": "espresso", "category": "hot drinks", "sizes": "single shot", "extras": "milk"}']
        
        assistant = None

        print("output      : ", reply)
        print("expected_out: ", expected_output)
        assert reply == expected_output

    
    @pytest.mark.repeat(1)
    @pytest.mark.parametrize("order_input", [
        "a single shot espresso with milk please!",
    ], indirect=True)
    def test_add_item_and_cancel_order(self, order_input):
        assistant = BeverageAssistant()
        response = assistant.run_order(order_input)
        
        reply = assistant.run_order("hmm I changed my mind. don't want anything anymore!")
        reply = reply[0]
        
        expected_output = []
        
        assistant = None

        print("output      : ", reply)
        print("expected_out: ", expected_output)
        assert reply == expected_output
    

    @pytest.mark.repeat(1)
    @pytest.mark.parametrize("order_input", [
        "a single shot espresso with milk please!",
    ], indirect=True)
    def test_add_multiple_available_orders(self, order_input):
        assistant = BeverageAssistant()
        response = assistant.run_order(order_input)
        
        reply = assistant.run_order("I also want to add a small hot chocolate with extra milk?")
        
        reply = reply[0]
        
        
        if "extra milk" in reply[1]:
            reply[1] = reply[1].replace("extra milk", "milk")


        if "single shot" in reply[0]:
            reply[0] = reply[0].replace("single shot", "single")

        expected_output = ['{"name": "espresso", "category": "hot drinks", "sizes": "single", "extras": "milk"}',
        '{"name": "hot chocolate", "category": "hot drinks", "sizes": "small", "extras": "milk"}']
        
        
        assistant = None

        print("output      : ", reply)
        print("expected_out: ", expected_output)
        assert reply == expected_output