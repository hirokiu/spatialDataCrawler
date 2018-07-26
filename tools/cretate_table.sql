-- Create syntax for TABLE 'area_hashtag'
CREATE TABLE `area_hashtag` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `hashtag` varchar(128) DEFAULT '',
  `count` bigint(20) DEFAULT NULL,
  `crawled_count` bigint(20) DEFAULT NULL,
  `area` varchar(128) DEFAULT NULL,
  `country` varchar(128) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Create syntax for TABLE 'entities'
CREATE TABLE `entities` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `url` varchar(256) NOT NULL DEFAULT '',
  `photo_url` varchar(256) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  `text` text,
  `hashtag_id` int(11) DEFAULT NULL,
  `hashtags` text,
  `location_id` int(11) DEFAULT NULL,
  `poi` point DEFAULT NULL,
  `timestamp` timestamp NULL DEFAULT NULL,
  `service` tinyint(2) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Create syntax for TABLE 'locations'
CREATE TABLE `locations` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `url` varchar(256) DEFAULT NULL,
  `poi` point DEFAULT NULL,
  `service` int(2) DEFAULT NULL,
  `district` varchar(128) DEFAULT NULL,
  `country` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Create syntax for TABLE 'user'
CREATE TABLE `user` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` varchar(256) DEFAULT NULL,
  `url` varchar(256) DEFAULT NULL,
  `username` varchar(128) DEFAULT NULL,
  `base_location` varchar(128) DEFAULT NULL,
  `service` int(2) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
