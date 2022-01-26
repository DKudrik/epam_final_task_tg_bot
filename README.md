# бейдж

# Picture_process_bot

Visit the project at https://t.me/picture_process_bot

### Picture process bot serves for:
  * Adding the entered text on a picture (you can choose a font/font size).
  * Creating a GIF from several pictures (you can choose if the GIF should be private - it      would be shown only to the sender. Also a watemark is added on the every GIF).
  * Sending all the GIFs created by the users (except of private GIFs).
  * Sending all the GIFs to the user created by him.


### Prerequisites

  Docker, Python installed

### Installing

To start a project:
  1. Register a telegram bot and get a key id and a secret key.
  1. Type 'docker-compose up' in terminal
  2. Go to api_yamdb container and aplly migrations

  * To get into a container with postgres DB or with api_yamdb project open a new terminal tab
   and type 'docker ps', then choose ID of the container and type 'docker exec -it    <container_id> bash'
  *  To create a superuser in api_yamdb container type 'python manage.py createsuper'
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
