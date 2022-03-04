CREATE DATABASE  IF NOT EXISTS `stockexchangesimulator` /*!40100 DEFAULT CHARACTER SET latin1 */;
USE `stockexchangesimulator`;
-- MySQL dump 10.13  Distrib 8.0.26, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: stockexchangesimulator
-- ------------------------------------------------------
-- Server version	5.5.48

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `transactions`
--

DROP TABLE IF EXISTS `transactions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `transactions` (
  `date_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `username` varchar(30) NOT NULL,
  `stock_symbol` varchar(30) NOT NULL,
  `num_shares` int(11) NOT NULL,
  `price` float NOT NULL,
  KEY `username` (`username`),
  CONSTRAINT `transactions_ibfk_1` FOREIGN KEY (`username`) REFERENCES `users` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `transactions`
--

LOCK TABLES `transactions` WRITE;
/*!40000 ALTER TABLE `transactions` DISABLE KEYS */;
INSERT INTO `transactions` VALUES ('2022-02-01 15:30:50','stonks_SA','AAPL',2,175),('2022-02-01 15:37:17','stonks_SA','AAPL',2,174.78),('2022-02-01 15:42:53','stonks_SA','AAPL',4,174.78),('2022-02-01 15:44:42','stonks_SA','AAPL',4,174.78),('2022-02-01 15:45:16','stonks_SA','AAPL',2,174.78),('2022-02-01 15:46:46','stonks_SA','AAPL',2,174.78),('2022-02-01 15:46:46','stonks_SA','AAPL',2,174.78),('2022-02-01 15:48:09','stonks_SA','AAPL',3,174.78),('2022-02-01 17:49:20','stonks_SA','NFLX',4,427.14),('2022-02-01 17:52:50','stonks_SA','NFLX',-2,427.14),('2022-02-01 18:13:50','stonks_SA','AAPL',-2,173.13),('2022-02-01 19:07:52','stonks_SA2','XIACF',4,2.15),('2022-02-01 19:09:43','stonks_SA2','XIACF',-3,2.15),('2022-02-01 19:11:06','stonks_SA2','AAPL',3,173.1),('2022-02-02 07:27:06','stonks_SA','AAPL',2,174.61),('2022-02-02 07:51:09','stonks_SA','AAPL',2,174.61),('2022-02-03 09:12:08','stonks_SA','XIACF',5,2.2),('2022-02-03 09:12:42','stonks_SA','NFLX',-2,429.48),('2022-02-03 09:15:50','stonks_SA','NFLX',12,429.48),('2022-02-03 09:32:51','stonks_SA','AAPL',3,175.84),('2022-02-03 09:32:51','stonks_SA','AAPL',3,175.84),('2022-02-03 09:32:51','stonks_SA','AAPL',3,175.84);
/*!40000 ALTER TABLE `transactions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `username` varchar(30) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `API_KEY` varchar(255) NOT NULL,
  `cash` float NOT NULL DEFAULT '10000',
  PRIMARY KEY (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES ('stonks_SA','pbkdf2:sha256:260000$NWQjllpHgTxYGlYE$f4a7a86f939a9c732e6bc5f81ba39fb86c5d2e62857edf0de69025010b0f6cc7','pk_1a3f7fb83f854378aa8ef510eddeeb06',638.96),('stonks_SA2','pbkdf2:sha256:260000$9mySMKdU8hpFFtC7$d36fef48826bf5b7f1730e01fee556e45759943de738b536f6a53e5ca0508e7f','pk_1a3f7fb83f854378aa8ef510eddeeb06',9478.55),('Talha','pbkdf2:sha256:260000$cbVrukebVgjPXJUQ$ed17e70048ee49ba1125f3aefff04d5d0b07cedfbbd49c4601c07233f75ef75f','pk_1a3f7fb83f854378aa8ef510eddeeb06',10000);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2022-03-04 18:13:16
