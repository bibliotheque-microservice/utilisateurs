version: '3.8'
services:
  flask_app:
    build: .
    ports:
      - "5000:5000"
    depends_on:
      - mariadb_db
    environment:
      - DATABASE_URI=mysql+pymysql://username:password@mariadb_db:3306/user_db

  mariadb_db:
    image: mariadb:10.5
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_USER: username
      MYSQL_PASSWORD: password
      MYSQL_DATABASE: user_db
    ports:
      - "3306:3306"
