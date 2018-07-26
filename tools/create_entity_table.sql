CREATE TABLE `entities` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `photo_id` bigint(128) DEFAULT NULL,
  `shortcode` varchar(45) NOT NULL,
  `url` varchar(256) NOT NULL DEFAULT '',
  `photo_url` varchar(256) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  `text` text,
  `hashtag_id` int(11) DEFAULT NULL,
  `hashtags` text,
  `location_id` bigint(20) DEFAULT NULL,
  `poi` geometry DEFAULT NULL,
  `timestamp` timestamp NULL DEFAULT NULL,
  `service` tinyint(2) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8

CREATE TABLE `locations` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `location_id` bigint(128) NOT NULL,
  `url` varchar(256) DEFAULT NULL,
  `name` varchar(128) DEFAULT NULL,
  `geo` geometry NOT NULL,
  `service` int(2) DEFAULT NULL,
  `district` varchar(128) DEFAULT NULL,
  `country` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`id`),
  SPATIAL KEY `geo` (`geo`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8
