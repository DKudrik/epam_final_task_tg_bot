# Picture_process_bot

Visit the project at https://t.me/picture_process_bot

### Picture process bot serves for:
  * Adding the entered text on a picture (you can choose a font/font size).
  * Creating a GIF from several pictures (you can choose if the GIF should be private - it would be shown only to the sender. Also a watemark is added on the every GIF).
  * Sending all the GIFs created by the users (except of private GIFs).
  * Sending all the GIFs to the user created by him.

  List of commands:
  * /start - to request the greeting message


### Prerequisites

  Docker installed

### Installing

To start a project:
  1. Register a telegram bot and get a token. Put it in the .env file under "bot_token" name
  2. Register a bucket in the Yandex Object Storage and get a key id and a secret key. Put them
     in the .env file under "aws_access_key_id" and "aws_secret_access_key" names
  3. If needed changed MongoDB login and password
  4. New fonts should be added to "fonts" folder (names should only contain letters and numbers)
  5. To start, type in the terminal "docker-compose up".


## Built With

* [Python](https://www.python.org/) - Programming language used
* [Docker](https://maven.apache.org/) - Platform to deliver software in packages (containers)
* [Yandex Object Storage](https://cloud.yandex.com/en/docs/storage/) - Yandex S3 storage
* [Telegram](https://web.telegram.org/z/) - Cloud-based mobile and desktop messaging app

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Authors

* **Denis Kudrik** - *Initial work* - [DKudrik](https://github.com/DKudrik/epam_final_task_tg_bot)

## License

This project is licensed under the MIT License
