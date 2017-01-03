# ************************************************************
# Sequel Pro SQL dump
# Version 4541
#
# http://www.sequelpro.com/
# https://github.com/sequelpro/sequelpro
#
# Host: localhost (MySQL 5.6.26)
# Database: google_play
# Generation Time: 2017-01-03 01:15:35 +0000
# ************************************************************


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


# Dump of table category
# ------------------------------------------------------------

DROP TABLE IF EXISTS `category`;

CREATE TABLE `category` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `category` varchar(64) NOT NULL DEFAULT '',
  `status` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

LOCK TABLES `category` WRITE;
/*!40000 ALTER TABLE `category` DISABLE KEYS */;

INSERT INTO `category` (`id`, `category`, `status`)
VALUES
	(1,'ANDROID_WEAR',0),
	(2,'ART_AND_DESIGN',0),
	(3,'AUTO_AND_VEHICLES',0),
	(4,'BEAUTY',0),
	(5,'BOOKS_AND_REFERENCE',0),
	(6,'BUSINESS',0),
	(7,'COMICS',0),
	(8,'COMMUNICATION',0),
	(9,'DATING',0),
	(10,'EDUCATION',0),
	(11,'ENTERTAINMENT',0),
	(12,'EVENTS',0),
	(13,'FINANCE',0),
	(14,'FOOD_AND_DRINK',0),
	(15,'HEALTH_AND_FITNESS',0),
	(16,'HOUSE_AND_HOME',0),
	(17,'LIBRARIES_AND_DEMO',0),
	(18,'LIFESTYLE',0),
	(19,'MAPS_AND_NAVIGATION',0),
	(20,'MEDICAL',0),
	(21,'MUSIC_AND_AUDIO',0),
	(22,'NEWS_AND_MAGAZINES',0),
	(23,'PARENTING',0),
	(24,'PERSONALIZATION',0),
	(25,'PHOTOGRAPHY',0),
	(26,'PRODUCTIVITY',0),
	(27,'SHOPPING',0),
	(28,'SOCIAL',0),
	(29,'SPORTS',0),
	(30,'TOOLS',0),
	(31,'GAME_ACTION',0),
	(32,'GAME_ADVENTURE',0),
	(33,'GAME_ARCADE',0),
	(34,'GAME_BOARD',0),
	(35,'GAME_CARD',0),
	(36,'GAME_CASINO',0),
	(37,'GAME_CASUAL',0),
	(38,'GAME_EDUCATIONAL',0),
	(39,'GAME_MUSIC',0),
	(40,'GAME_PUZZLE',0),
	(41,'GAME_RACING',0),
	(42,'GAME_ROLE_PLAYING',0),
	(43,'GAME_SIMULATION',0),
	(44,'GAME_SPORTS',0),
	(45,'GAME_STRATEGY',0),
	(46,'GAME_TRIVIA',0),
	(47,'GAME_WORD',0),
	(48,'FAMILY?age=AGE_RANGE1',0),
	(49,'FAMILY?age=AGE_RANGE2',0),
	(50,'FAMILY?age=AGE_RANGE3',0),
	(51,'FAMILY_ACTION',0),
	(52,'FAMILY_BRAINGAMES',0),
	(53,'FAMILY_CREATE',0),
	(54,'FAMILY_EDUCATION',0),
	(55,'FAMILY_MUSICVIDEO',0),
	(56,'FAMILY_PRETEND',0),
	(57,'TRAVEL_AND_LOCAL',0),
	(58,'VIDEO_PLAYERS',0),
	(59,'WEATHER',0);

/*!40000 ALTER TABLE `category` ENABLE KEYS */;
UNLOCK TABLES;


# Dump of table developer
# ------------------------------------------------------------

DROP TABLE IF EXISTS `developer`;

CREATE TABLE `developer` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(128) NOT NULL DEFAULT '',
  `status` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table key_word
# ------------------------------------------------------------

DROP TABLE IF EXISTS `key_word`;

CREATE TABLE `key_word` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `key_word` varchar(128) NOT NULL DEFAULT '',
  `status` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `key_word` (`key_word`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table package_name
# ------------------------------------------------------------

DROP TABLE IF EXISTS `package_name`;

CREATE TABLE `package_name` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `package_name` varchar(128) NOT NULL DEFAULT '',
  `status` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `package_name` (`package_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table raw_text
# ------------------------------------------------------------

DROP TABLE IF EXISTS `raw_text`;

CREATE TABLE `raw_text` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `text` text NOT NULL,
  `status` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table similar_app
# ------------------------------------------------------------

DROP TABLE IF EXISTS `similar_app`;

CREATE TABLE `similar_app` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `package_name` varchar(128) NOT NULL DEFAULT '',
  `status` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `package_name` (`package_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;




/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
