# Multi-turn prompt

Bot Framework v4 multi-turn prompt bot sample

This bot has been created using [Bot Framework](https://dev.botframework.com), it shows how to use the prompts classes included in `botbuilder-dialogs`. This bot will ask for the user's name and age, then store the responses. It demonstrates a multi-turn dialog flow using a text prompt, a number prompt, and state accessors to store and retrieve values.

## To try this sample

- Clone the repository

```bash
git clone https://github.com/Microsoft/botbuilder-samples.git
```

- In a terminal, navigate to `botbuilder-samples\samples\python\05.multi-turn-prompt` folder
- Activate your desired virtual environment
- In the terminal, type `pip install -r requirements.txt`
- Run your bot with `python app.py`

## Testing the bot using Bot Framework Emulator

[Bot Framework Emulator](https://github.com/microsoft/botframework-emulator) is a desktop application that allows bot developers to test and debug their bots on localhost or running remotely through a tunnel.

- Install the latest Bot Framework Emulator from [here](https://github.com/Microsoft/BotFramework-Emulator/releases)

### Connect to the bot using Bot Framework Emulator

- Launch Bot Framework Emulator
- File -> Open Bot
- Enter a Bot URL of `http://localhost:3978/api/messages`

## Interacting with the bot

A conversation between a bot and a user often involves asking (prompting) the user for information, parsing the user's response,
and then acting on that information. This sample demonstrates how to prompt users for information using the different prompt types
included in the [botbuilder-dialogs](https://docs.microsoft.com/en-us/azure/bot-service/bot-builder-concept-dialog?view=azure-bot-service-4.0) library
and supported by the SDK.

The `botbuilder-dialogs` library includes a variety of pre-built prompt classes, including text, number, and datetime types. This
sample demonstrates using a text prompt to collect the user's name, then using a number prompt to collect an age.

## Deploy the bot to Azure

To learn more about deploying a bot to Azure, see [Deploy your bot to Azure](https://aka.ms/azuredeployment) for a complete list of deployment instructions.

### Provision the bot resources

1. az ad app create --display-name "ins-verification-bot" --password "Bandera01" --available-to-other-tenant

   - appId: 2a896a89-7bd3-4e9f-a939-f8754d5737b2
   - password: Bandera01

2. az deployment sub create --template-file ""C:\Users\zachl\Codes\test-azure-deployment\my_chat_bot\deploymentTemplates\template-with-new-rg.json"" --location eastus --parameters appType="MultiTenant" appId="2a896a89-7bd3-4e9f-a939-f8754d5737b2" appSecret="Bandera01" botId="ut-ins-bot-production" botSku=F0 newAppServicePlanName="ut-ins-bot-app-service" newWebAppName="ut-ins-bot-web-app" groupName="ut-ins-bot-app" groupLocation="eastus" newAppServicePlanLocation="eastus" newAppServicePlanSku=F0 --name "ut-ins-bot-production"

   - using the other test deployment template b/c might have messed this one up
   - also add the AppPlanSku as F0 -> delete this actually

3. Release the actual build

## Further reading

- [Bot Framework Documentation](https://docs.botframework.com)
- [Bot Basics](https://docs.microsoft.com/azure/bot-service/bot-builder-basics?view=azure-bot-service-4.0)
- [Dialogs](https://docs.microsoft.com/en-us/azure/bot-service/bot-builder-concept-dialog?view=azure-bot-service-4.0)
- [Gathering Input Using Prompts](https://docs.microsoft.com/en-us/azure/bot-service/bot-builder-prompts?view=azure-bot-service-4.0&tabs=csharp)
- [Activity processing](https://docs.microsoft.com/en-us/azure/bot-service/bot-builder-concept-activity-processing?view=azure-bot-service-4.0)
- [Azure Bot Service Introduction](https://docs.microsoft.com/azure/bot-service/bot-service-overview-introduction?view=azure-bot-service-4.0)
- [Azure Bot Service Documentation](https://docs.microsoft.com/azure/bot-service/?view=azure-bot-service-4.0)
- [Azure CLI](https://docs.microsoft.com/cli/azure/?view=azure-cli-latest)
- [Azure Portal](https://portal.azure.com)
- [Channels and Bot Connector Service](https://docs.microsoft.com/en-us/azure/bot-service/bot-concepts?view=azure-bot-service-4.0)
