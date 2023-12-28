from openai import AzureOpenAI
import json
import os
from dotenv import load_dotenv

class BeverageAssistant:
    def __init__(self):
        load_dotenv()
        self.order_list = []
        self.system_role = "You are a beverage machine assistant helping to take orders and submit them. You are not preparing anything. Only taking orders according to what is available and if not you let the user know. If you don't understand the request ask for clarification. Always ask for further request at the end of your responses until the user is submitting the order. Don't guess any information and ask for details. For example, if the user is asking for an espresso don't guess the size and ask for clarification."

        self.client = AzureOpenAI(
            azure_endpoint=os.getenv("OPENAI_AZURE_ENDPOINT"),
            api_version=os.getenv("OPENAI_API_VERSION", "2023-12-01-preview"),
            api_key=os.getenv("OPENAI_API_KEY")
        )

        self.messages = [{"role": "system", "content": self.system_role}]

        self.products = [
            {
                "name": "Caffè Crema",
                "category": "Hot drinks",
                "sizes": ["small", "medium", "large"],
                "extras": ["milk", "sugar"]
            },
            {
                "name": "Espresso",
                "category": "Hot drinks",
                "sizes": ["single", "double"],
                "extras": ["milk", "sugar"]
            },
            {
                "name": "Cappuccino",
                "category": "Hot drinks",
                "extras": ["milk", "sugar"],
                "sizes": ["small", "medium", "large"],
            },
            {
                "name": "Latte Macchiato",
                "category": "Hot drinks",
                "extras": ["milk", "sugar"]
            },
            {
                "name": "Hot Chocolate",
                "category": "Hot drinks",
                "extras": ["milk", "sugar"],
                "sizes": ["small", "medium", "large"]
            },
        ]

        self.function_descriptions = [
            {
                "name": "add_item",
                "description": "Add orders to the order basket. Get item information and add them to the order basket. If there was a drink in the prompt maybe also needs to be included in the order basket. e.g coffee too. offer to show the list of available items in case the customer is looking for an item that is not available.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "The name of or type of beverage",
                        },
                        "category": {
                            "type": "string",
                            "description": "The category of the drinks, e.g. hot drinks or cold",
                        },
                        "sizes": {
                            "type": "string",
                            "description": "The size of the drinks e.g. small or big or amount of espresso, e.g. single or double shot ",
                        },
                        "extras": {
                            "type": "string",
                            "description": "Any extras to add to the drink like milk or sugar",
                        }
                    },
                    "required": ["name", "category", "sizes", "extras"],
                },
            },
            {
                "name": "remove_item",
                "description": "Removes the Item specified from the order basket",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "The name of drink to be removed",
                        },
                    },
                    "required": ["name"],
                }
            },
            {
                "name": "cancel_order",
                "description": "Cancels the order completely",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "cancel": {
                            "type": "string",
                            "description": "Any type of word that refers to canceling an order!, e.g cancel, decline, that's it, thanks I'm good and etc",
                        },
                    },
                    "required": ["cancel"],
                }
            },
            {
                "name": "submit_order",
                "description": "Submits the order. Any way of saying that I'm done with giving the orders and now I want to submit and proceed with it, e.g. submit, proceed with payment, or that's all thanks, or thanks that's all I wanted, I'm good with this and etc.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "submit": {
                            "type": "string",
                            "description": "Any type of word that refers to end the ordering process and proceeding with the payment",
                        },
                    },
                    "required": ["submit"],
                }
            },
            {
                "name": "show_available_items",
                "description": "Lists the available products to offer to the customer",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            }
        ]

    def ask_and_reply(self, messages, function_call):
        completion = self.client.chat.completions.create(
            model="gpt35-613-ak-trial",
            messages=messages,
            functions=self.function_descriptions,
            function_call=function_call,
        )
        output = completion.choices[0].message
        return output

    def add_item(self, name, category, sizes, extras):
        name = name.lower()
        category = category.lower()

        for product in self.products:
            if product["name"].lower() == name and product["category"].lower() == category:
                if sizes == "" or sizes is None:
                    return f"Missing information about size"

                if extras == "" or extras is None:
                    return f"Missing information about extras"
                order_details = {
                    "name": name,
                    "category": category,
                    "sizes": sizes,
                    "extras": extras,
                }

                self.order_list.append(json.dumps(order_details))
                return json.dumps(order_details)

        return f"{name} is not available at the moment"

    def remove_item(self, name):
        for item in self.order_list:
            item_dict = eval(item)

            if item_dict["name"].lower() == name.lower():
                self.order_list.remove(item)
                return f"{item} removed"
            else:
                return "The item doesn't exist in the order basket"

    def cancel_order(self, cancel):
        self.order_list[:] = []
        return f"Order is canceled! Remove all items in the order basket"

    def submit_order(self, submit):
        return f"Order {self.order_list} is submitted!"

    def show_available_items(self, none):
        return f"Here are the available items {self.products}"

    def run_order(self, prompt):
        user_prompt = prompt
        print("User Prompt: ", user_prompt)

        self.messages.append({"role": "user", "content": user_prompt})
        response = self.ask_and_reply(messages=self.messages, function_call="auto")
        
        if response.function_call:
            
            if response.function_call.name == "show_available_items":
                params = json.loads(response.function_call.arguments)
                chosen_function = getattr(self, response.function_call.name)
                order = chosen_function(None)
                self.messages.append({"role": "function", "name": response.function_call.name, "content": order})
                reply = self.ask_and_reply(messages=self.messages, function_call="auto")
                self.messages = self.messages[1:]
                print("Assistant:", reply.content)

            params = json.loads(response.function_call.arguments)
            chosen_function = getattr(self, response.function_call.name)

            if params == {}:
                order = chosen_function(None)
            else:
                order = chosen_function(**params)
                
            if order == None:
                order = ""

            self.messages.append({"role": "function", "name": response.function_call.name, "content": order})
            reply = self.ask_and_reply(messages=self.messages, function_call="auto")
            print("Assistant:", reply.content)

        print("Final Order List:", self.order_list)
        print("\n\n")
        return self.order_list, response



class ResponseValidator:
    def __init__(self):
        load_dotenv()
        self.client = AzureOpenAI(
            azure_endpoint=os.getenv("OPENAI_AZURE_ENDPOINT"),
            api_version=os.getenv("OPENAI_API_VERSION", "2023-12-01-preview"),
            api_key=os.getenv("OPENAI_API_KEY")
        )

        # Define function descriptions for validation
        self.function_descriptions = [
            {
                "name": "validate_response",
                "description": "Validate the response generated by the assistant.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "response": {
                            "type": "object",
                            "description": "The response to be validated.",
                        },
                    },
                    "required": ["response"],
                },
            }
            # Add other function descriptions as needed
        ]

    def validate_response(self, assistant, response):
        if response.function_call:
            # Validate the function call
            function_name = response.function_call.name
            params = json.loads(response.function_call.arguments)

            # Check if the function exists in the assistant class
            if not hasattr(assistant, function_name):
                return f"Error: Function '{function_name}' does not exist in the assistant class."


            # Validate the response using an LLM
            validation_prompt = f"Validate the response: {response}" # TODO: maybe pass the teest scenarios completely
            # TODO: extend the defenition of the llm validator to use this scenarios
            
            validation_result = self.validate_with_llm(validation_prompt, response.function_call)

            return validation_result

        return "Response validation successful."

    def validate_with_llm(self, prompt, function_call="auto"):
        messages = [{"role": "system", "content": "You are a response validation assistant."}]
        if function_call:
            messages.append({"role": "function", "name": "validate_response", "content": prompt})

        print("messages: ", messages)
        completion = self.client.chat.completions.create(
            model="gpt35-613-ak-trial",
            messages=messages,
            functions=self.function_descriptions,
            function_call=function_call,
        )
        print("blabla:    ", completion)
        validation_result = completion.choices[0].message.content
        return validation_result

# Example usage:
assistant = BeverageAssistant()
validator = ResponseValidator()


order_prompt = "I want a single shot espresso with milk please"
order_result, response = assistant.run_order(order_prompt)

validation_result = validator.validate_response(assistant, response)
