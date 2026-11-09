-- MySQL dump 10.13  Distrib 8.0.46, for Win64 (x86_64)
--
-- Host: localhost    Database: trustvault
-- ------------------------------------------------------
-- Server version	8.0.46

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `audit_logs`
--

DROP TABLE IF EXISTS `audit_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `audit_logs` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `actor_id` int DEFAULT NULL,
  `document_id` int DEFAULT NULL,
  `action` varchar(50) NOT NULL,
  `result` varchar(20) NOT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  `event_data` json DEFAULT NULL,
  `previous_hash` char(64) DEFAULT NULL,
  `event_hash` char(64) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `actor_id` (`actor_id`),
  KEY `document_id` (`document_id`),
  CONSTRAINT `audit_logs_ibfk_1` FOREIGN KEY (`actor_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `audit_logs_ibfk_2` FOREIGN KEY (`document_id`) REFERENCES `documents` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `audit_logs`
--

LOCK TABLES `audit_logs` WRITE;
/*!40000 ALTER TABLE `audit_logs` DISABLE KEYS */;
INSERT INTO `audit_logs` VALUES (1,1,1,'document_upload','success','127.0.0.1','{\"filename\": \"suneel_resume.pdf\"}',NULL,'b237807195310c21eecc66e7600a589ee8378227e6cfe4ca9db2b0a078ecca32','2026-11-05 17:25:13'),(2,1,1,'document_download','success','127.0.0.1','{\"filename\": \"suneel_resume.pdf\"}','b237807195310c21eecc66e7600a589ee8378227e6cfe4ca9db2b0a078ecca32','1961ef24271d0a99687fabe98f11299e81beb7a5e1ed723e1685228048b7ea95','2026-11-05 17:26:37');
/*!40000 ALTER TABLE `audit_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `categories`
--

DROP TABLE IF EXISTS `categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categories` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categories`
--

LOCK TABLES `categories` WRITE;
/*!40000 ALTER TABLE `categories` DISABLE KEYS */;
INSERT INTO `categories` VALUES (2,'Finance'),(4,'HR'),(3,'Legal'),(6,'Other'),(1,'Personal'),(5,'Technical');
/*!40000 ALTER TABLE `categories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `documents`
--

DROP TABLE IF EXISTS `documents`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `documents` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `original_filename` varchar(255) NOT NULL,
  `storage_key` varchar(255) NOT NULL,
  `mime_type` varchar(100) NOT NULL,
  `size_bytes` bigint NOT NULL,
  `sha256` char(64) DEFAULT NULL,
  `owner_id` int NOT NULL,
  `category_id` int DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `storage_key` (`storage_key`),
  KEY `owner_id` (`owner_id`),
  KEY `category_id` (`category_id`),
  CONSTRAINT `documents_ibfk_1` FOREIGN KEY (`owner_id`) REFERENCES `users` (`id`),
  CONSTRAINT `documents_ibfk_2` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `documents`
--

LOCK TABLES `documents` WRITE;
/*!40000 ALTER TABLE `documents` DISABLE KEYS */;
INSERT INTO `documents` VALUES (1,'resume','suneel_resume.pdf','ca74e27bb5e549a8bfa8f60bc114fe92.pdf','application/pdf',90234,'f47a4f07a0027ad66eebf8aa87ecd5a240706b2d0c655cf992631054dee88d39',1,5,'2026-11-05 17:25:13','2026-11-05 17:25:13');
/*!40000 ALTER TABLE `documents` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `permissions`
--

DROP TABLE IF EXISTS `permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `permissions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `document_id` int NOT NULL,
  `user_id` int NOT NULL,
  `granted_by` int NOT NULL,
  `permission_type` varchar(10) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `document_id` (`document_id`,`user_id`),
  KEY `user_id` (`user_id`),
  KEY `granted_by` (`granted_by`),
  CONSTRAINT `permissions_ibfk_1` FOREIGN KEY (`document_id`) REFERENCES `documents` (`id`),
  CONSTRAINT `permissions_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `permissions_ibfk_3` FOREIGN KEY (`granted_by`) REFERENCES `users` (`id`),
  CONSTRAINT `permissions_chk_1` CHECK ((`permission_type` in (_utf8mb4'read',_utf8mb4'edit')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `permissions`
--

LOCK TABLES `permissions` WRITE;
/*!40000 ALTER TABLE `permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `email` varchar(150) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `role` varchar(20) NOT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  CONSTRAINT `chk_user_role` CHECK ((`role` in (_utf8mb4'admin',_utf8mb4'owner',_utf8mb4'viewer')))
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'TrustVault Admin','admin@trustvault.local','scrypt:32768:8:1$kjqaGCuZq6gwHtin$4e734bc8d8afd91dea6658994b1affcd8c5af7615fa889397524f8513bccedcfc07b84a7e576c04e333232cd6eb7c877f8ca5e49d36cd3be8a95e13bda0b5866','admin',1,'2026-11-05 14:09:40'),(2,'Document Owner','owner@trustvault.local','scrypt:32768:8:1$aQoxr1iFrfcwnrr2$2f122ab3a2edcab88b108f2b471797935fc76dc91444cb0febd66d34ca295005bd1c45ed2ea34ab837d625fe8f46150545bae5585ccb7635c383335d2f32aeaa','owner',1,'2026-11-05 14:09:40'),(3,'Document Viewer','viewer@trustvault.local','scrypt:32768:8:1$MLn6DVJLVb2sKz0L$c2486ff63fd077739344b224995795a65d756e66a35df44965e053c77d8d1de0ac781ca3640eb2d6ec4e031f7d177e23bca1baefea31a3fe22542f0de6e2fae8','viewer',1,'2026-11-05 14:09:40');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'trustvault'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-11-09 10:50:40
