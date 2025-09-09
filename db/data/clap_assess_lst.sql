-- MySQL dump 10.13  Distrib 8.0.43, for Win64 (x86_64)
--
-- Host: localhost    Database: clap
-- ------------------------------------------------------
-- Server version	8.0.43

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
-- Table structure for table `assess_lst`
--

DROP TABLE IF EXISTS `assess_lst`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `assess_lst` (
  `PATIENT_ID` char(4) NOT NULL,
  `ORDER_NUM` int unsigned NOT NULL,
  `REQUEST_ORG` varchar(100) DEFAULT NULL,
  `ASSESS_DATE` date DEFAULT NULL,
  `ASSESS_PERSON` varchar(50) DEFAULT NULL,
  `AGE` smallint DEFAULT NULL,
  `EDU` smallint DEFAULT NULL,
  `EXCLUDED` char(1) DEFAULT NULL,
  `POST_STROKE_DATE` date DEFAULT NULL,
  `DIAGNOSIS` char(1) DEFAULT NULL,
  `DIAGNOSIS_ETC` varchar(100) DEFAULT NULL,
  `STROKE_TYPE` char(1) DEFAULT NULL,
  `LESION_LOCATION` varchar(100) DEFAULT NULL,
  `HEMIPLEGIA` varchar(5) DEFAULT NULL,
  `HEMINEGLECT` varchar(5) DEFAULT NULL,
  `VISUAL_FIELD_DEFECT` varchar(5) DEFAULT NULL,
  `CREATE_DATE` datetime DEFAULT CURRENT_TIMESTAMP,
  `UPDATE_DATE` datetime DEFAULT NULL,
  PRIMARY KEY (`PATIENT_ID`,`ORDER_NUM`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='평가 목록';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `assess_lst`
--

LOCK TABLES `assess_lst` WRITE;
/*!40000 ALTER TABLE `assess_lst` DISABLE KEYS */;
INSERT INTO `assess_lst` VALUES ('1001',1,'충북대','2025-02-05','구혜영',43,16,'0','2022-10-25','1',NULL,'2','10022863','2',NULL,NULL,'2025-08-08 15:40:20',NULL),('1002',1,NULL,NULL,NULL,0,NULL,'1',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-08-08 15:40:20',NULL),('1003',1,'충북대','2025-02-06','구혜영',78,6,'0','2025-01-27','0',NULL,'0','07808919','2',NULL,NULL,'2025-08-08 15:40:20',NULL),('1004',1,'충북대','2025-02-06','구혜영',69,12,'0','2025-02-03',NULL,NULL,NULL,'06065924',NULL,NULL,NULL,'2025-08-08 15:40:20',NULL),('1005',1,NULL,NULL,NULL,0,NULL,'1',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-08-08 15:40:20',NULL),('1015',1,'충북대','2025-02-12','구혜영',46,16,'0',NULL,'1',NULL,'1','03614916',NULL,NULL,NULL,'2025-08-08 15:40:20',NULL),('1023',1,'충북대','2025-02-17','구혜영',69,12,'0','2006-10-08','1',NULL,'1','00776383','0',NULL,NULL,'2025-08-08 15:40:20',NULL),('1024',1,'충북대','2025-02-17','구혜영',64,6,'0','2025-02-13','0',NULL,'0','10454901','2',NULL,NULL,'2025-08-08 15:40:20',NULL),('1025',1,'충북대','2025-02-17','구혜영',69,6,'0','2025-02-13','0',NULL,'1','08970846','2',NULL,NULL,'2025-08-08 15:40:20',NULL),('1026',1,'충북대','2025-02-18','구혜영',63,14,'0','2025-02-14','0',NULL,'0','05418877','2',NULL,NULL,'2025-08-08 15:40:20',NULL),('1027',1,'충북대','2025-02-18','구혜영',86,12,'0','2025-02-14','0',NULL,'2','10471987','2',NULL,NULL,'2025-08-08 15:40:20',NULL),('1031',1,NULL,NULL,NULL,0,16,'1',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-08-08 15:40:20',NULL),('1032',1,'충북대','2025-02-20','구혜영',73,12,'0','2025-02-14','0',NULL,'2','10601137','2',NULL,NULL,'2025-08-08 15:40:20',NULL),('1033',1,'충북대','2025-02-25','구혜영',72,16,'0','2025-02-20','0',NULL,'0','10601442','1',NULL,NULL,'2025-08-08 15:40:20',NULL),('1034',1,'충북대','2025-02-25','구혜영',76,12,'0','2025-02-20','0',NULL,'0','10572319','0',NULL,NULL,'2025-08-08 15:40:20',NULL),('1035',1,'충북대','2025-02-20','구혜영',80,12,'0','2025-01-27','0',NULL,'1','01604557','2',NULL,NULL,'2025-08-08 15:40:20',NULL),('1036',1,'충북대','2025-02-21','구혜영',56,12,'0','2024-10-25','0',NULL,'0','10594460','2',NULL,NULL,'2025-08-08 15:40:20',NULL),('1042',1,'충북대','2025-02-26','구혜영',62,12,'0','2025-02-24','0',NULL,'1','04877178','2',NULL,NULL,'2025-08-08 15:40:20',NULL),('1043',1,'충북대','2025-02-26','구혜영',70,9,'0','2025-02-22','0',NULL,'2','01499595','0',NULL,NULL,'2025-08-08 15:40:20',NULL),('1044',1,NULL,NULL,NULL,0,NULL,'1',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-08-08 15:40:20',NULL),('1045',1,'충북대','2025-02-26','구혜영',65,16,'0','2023-05-05','1',NULL,'2','01631397','2',NULL,NULL,'2025-08-08 15:40:20',NULL),('1077',1,NULL,NULL,NULL,NULL,NULL,'1',NULL,NULL,NULL,NULL,'05068463',NULL,NULL,NULL,'2025-08-08 15:40:20',NULL),('1078',1,NULL,NULL,NULL,79,12,'1','2025-01-20',NULL,NULL,NULL,'00202824',NULL,NULL,NULL,'2025-08-08 15:40:20',NULL),('1079',1,NULL,NULL,NULL,84,6,'1','2025-01-15',NULL,NULL,NULL,'10599920',NULL,NULL,NULL,'2025-08-08 15:40:20',NULL),('2006',1,'씨엔씨','2025-02-07','구혜영',58,12,'0','2024-10-04','4','독성뇌병증',NULL,'씨엔씨',NULL,'2','2','2025-08-08 15:40:20',NULL),('2007',1,'씨엔씨','2025-02-10','구혜영',66,12,'0','2024-11-18','0',NULL,NULL,'씨엔씨',NULL,'2','2','2025-08-08 15:40:20',NULL),('2014',1,'씨엔씨','2025-02-11','구혜영',77,6,'0',NULL,NULL,NULL,NULL,'씨엔씨',NULL,'2','2','2025-08-08 15:40:20',NULL),('3008',1,'첼로','2025-02-20','구혜영',55,16,'0','2024-03-03','0',NULL,'1','Lt. cerebral infaction','0','2','2','2025-08-08 15:40:20',NULL),('3009',1,'첼로','2025-02-20','구혜영',70,16,'0','2023-09-30','1',NULL,'1','Lt. BG & CR ICH','0','2','2','2025-08-08 15:40:20',NULL),('3010',1,'첼로','2025-02-20','구혜영',64,12,'0','2024-12-01','3',NULL,NULL,'Pakinson disease','2','2','2','2025-08-08 15:40:20',NULL),('3011',1,'첼로','2025-02-20','구혜영',28,16,'0','2024-01-01','1',NULL,NULL,'cerebellar ICH','1','2','2','2025-08-08 15:40:20',NULL),('3012',1,NULL,NULL,NULL,0,12,'1','2024-09-22','0',NULL,'1','Lt. MCA ACA infaction','0','2','2','2025-08-08 15:40:20',NULL),('3013',1,NULL,NULL,NULL,0,12,'1','2023-12-25','0',NULL,'1','Lt. MCA ACA infaction','0','2','2','2025-08-08 15:40:20',NULL),('3016',1,NULL,'2025-02-13','구혜영',64,12,'1',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-08-08 15:40:20',NULL),('3017',1,'첼로','2025-02-13','구혜영',59,12,'0','2024-09-26','1',NULL,NULL,'첼로','0','2','2','2025-08-08 15:40:20',NULL),('3018',1,'첼로','2025-02-13','구혜영',44,12,'0','2024-01-13','0',NULL,NULL,'첼로',NULL,'2','2','2025-08-08 15:40:20',NULL),('3019',1,'첼로','2025-02-13','구혜영',65,12,'0','2024-08-31','1',NULL,NULL,'첼로','0','2','2','2025-08-08 15:40:20',NULL),('3020',1,NULL,'2025-02-13','구혜영',69,6,'0','2024-06-21','0',NULL,NULL,'첼로','0','2','2','2025-08-08 15:40:20',NULL),('3021',1,NULL,NULL,NULL,0,NULL,'1',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-08-08 15:40:20',NULL),('3022',1,'첼로','2025-02-13','구혜영',72,9,'0','2023-09-08','1',NULL,NULL,'첼로','0','2','2','2025-08-08 15:40:20',NULL),('3028',1,'첼로','2025-02-20','구혜영',66,16,'0','2024-02-23','1',NULL,NULL,'ICH','0','2','2','2025-08-08 15:40:20',NULL),('3029',1,'첼로','2025-02-20','구혜영',72,6,'0','2024-07-06','0',NULL,'1','Lt. BG infaction','0','2','2','2025-08-08 15:40:20',NULL),('3030',1,'첼로','2025-02-27','구혜영',69,16,'0','2024-09-10','0',NULL,'1','Lt. MCA infaction','0','2','2','2025-08-08 15:40:20',NULL),('3037',1,'첼로','2025-02-27','구혜영',67,9,'0','2023-12-21','0',NULL,'1','Lt. MCA infaction, Lt. high frontal lobe infaction','0','2','2','2025-08-08 15:40:20',NULL),('3038',1,'첼로','2025-02-27','구혜영',47,12,'0','2024-06-22','0',NULL,NULL,'MCA infaction','0','2','2','2025-08-08 15:40:20',NULL),('3039',1,'첼로','2025-02-27','구혜영',61,16,'0','2024-02-22','1',NULL,NULL,'cbr ICH','1','2','2','2025-08-08 15:40:20',NULL),('3040',1,'첼로','2025-02-27','구혜영',69,16,'0','2024-11-28','1',NULL,'1','Lt. ACA MCA infaction','0','2','2','2025-08-08 15:40:20',NULL),('3041',1,'첼로','2025-02-27','구혜영',65,6,'0','2024-06-02','1',NULL,NULL,'SAH w P-comAn rupuro ','1','2','2','2025-08-08 15:40:20',NULL),('3068',1,'첼로','2025-04-12','구혜영',38,12,'1','2023-07-20','1',NULL,'1','Rt. hemiplegia d/t Lt. BG & CR ICH','0','2','2','2025-08-08 15:40:20',NULL),('3069',1,'첼로','2025-04-12','구혜영',60,12,'1','2025-01-31','1',NULL,'1','Quadriplegia d/t Lt. BG ICH (2025.1.31) & old ICH  ','1','2','2','2025-08-08 15:40:20',NULL),('3070',1,'첼로','2025-04-12','구혜영',67,6,'0','2024-12-17','1',NULL,NULL,'Rt. hemiplegia and aphasia d/t cerebral ICH','0','2','2','2025-08-08 15:40:20',NULL),('3071',1,'첼로','2025-04-12','구혜영',67,6,'0','2024-08-09','0',NULL,'1','Rt. hemiplegia. aphasia. dysphagia d/t Lt. MCA infarction','0','2','2','2025-08-08 15:40:20',NULL),('3072',1,'첼로','2025-04-12','구혜영',42,14,'1','2024-11-19','1',NULL,'0','Left hemiplegia d/t Right BG ICH','1','2','2','2025-08-08 15:40:20',NULL),('3073',1,'첼로','2025-04-12','구혜영',65,6,'1','2024-10-23','0',NULL,'0','Lt hemiplegia d/t  Rt ant medullary infarction','1','2','2','2025-08-08 15:40:20',NULL),('3074',1,'첼로','2025-04-12','구혜영',53,12,'0','2025-02-23','1',NULL,'0','Rt. hemiplegia d/t cerebral ICH','0','2','2','2025-08-08 15:40:20',NULL),('3075',1,'첼로','2025-04-12','구혜영',62,14,'0','2025-02-04','0',NULL,'1','Gait disturbance d/t Left temporoparietal lobe infarction','2','2','2','2025-08-08 15:40:20',NULL),('3076',1,'첼로','2025-04-12','구혜영',69,12,'0','2025-02-15','0',NULL,'1','Rt. hemiplegia d/t Lt. PVWM infarction','0','2','2','2025-08-08 15:40:20',NULL),('4046',1,'아이엠','2025-03-15','구혜영',64,6,'0','2024-12-26','0',NULL,'1','아이엠','0','2','2','2025-08-08 15:40:20',NULL),('4047',1,'아이엠','2025-03-15','구혜영',52,9,'0','2024-09-30','1',NULL,NULL,'아이엠','2','2','2','2025-08-08 15:40:20',NULL),('4048',1,'아이엠','2025-03-15','구혜영',55,16,'1','2025-01-17','1',NULL,'0','아이엠','1','2','2','2025-08-08 15:40:20',NULL),('4049',1,'아이엠','2025-03-15','구혜영',74,6,'1','2024-08-08','0',NULL,'0','아이엠','1','2','2','2025-08-08 15:40:20',NULL),('4050',1,'아이엠','2025-03-15','구혜영',34,16,'1','2024-12-30','1',NULL,NULL,'아이엠','0','2','2','2025-08-08 15:40:20',NULL),('4051',1,NULL,NULL,NULL,71,NULL,'1','2024-08-19','1',NULL,'1','아이엠','0','2','2','2025-08-08 15:40:20',NULL),('4052',1,'아이엠','2025-03-15','구혜영',76,6,'0','2025-01-13','0',NULL,NULL,'아이엠','1','2','2','2025-08-08 15:40:20',NULL),('4053',1,'아이엠','2025-03-15','구혜영',85,5,'0','2023-11-25','0',NULL,'1','아이엠','0','2','2','2025-08-08 15:40:20',NULL),('4054',1,'아이엠','2025-03-15','구혜영',65,12,'0','2024-06-06','0',NULL,'1','아이엠','0','2','2','2025-08-08 15:40:20',NULL),('4055',1,'아이엠','2025-03-15','구혜영',64,6,'0','2024-12-01','1',NULL,'1','아이엠','0','2','2','2025-08-08 15:40:20',NULL),('4056',1,'아이엠','2025-03-15','구혜영',31,16,'0','2024-09-12','1',NULL,NULL,'아이엠','2','2','2','2025-08-08 15:40:20',NULL),('4057',1,'아이엠','2025-03-15','구혜영',38,16,'0','2024-02-18','1',NULL,'1','아이엠','0','2','2','2025-08-08 15:40:20',NULL),('5058',1,'마이크로','2025-03-29','구혜영',75,9,'0','2023-11-15','0',NULL,'1','Rt. hemiplegia d/t Lt. MCA infarction ','0','2','2','2025-08-08 15:40:20',NULL),('5059',1,'마이크로','2025-03-29','구혜영',0,12,'0','2025-02-12','0',NULL,'1','RT hemiplegia d/t Lt BG, F-P-O lobes infarction','0','0','0','2025-08-08 15:40:20',NULL),('5060',1,'마이크로','2025-03-29','구혜영',67,6,'0','2024-11-11','0',NULL,'1','Lt. hemiplegia d/t Cb. infarction with hemorrhagic transformation','1','2','2','2025-08-08 15:40:20',NULL),('5061',1,'마이크로','2025-03-29','구혜영',63,6,'0','2022-06-27','1',NULL,'1','Tetraplegia d/t SAH, ICH in Lt. frontal lobe  ','0,1','2','2','2025-08-08 15:40:20',NULL),('5062',1,'마이크로','2025-03-29','구혜영',77,0,'0','2025-01-08','0',NULL,'1','Rt. hemiplegia d/t Lt. BG infarction ','0','2','2','2025-08-08 15:40:20',NULL),('5063',1,'마이크로','2025-03-29','구혜영',68,12,'0','2025-01-22','1',NULL,'1','RT hemiplegia d/t ICH','0','2','2','2025-08-08 15:40:20',NULL),('5064',1,'마이크로','2025-03-29','구혜영',73,12,'0','2025-01-04','0',NULL,'1','Rt. hemiplegia d/t Lt. cerebral infarction','0','2','2','2025-08-08 15:40:20',NULL),('5065',1,'마이크로','2025-03-29','구혜영',67,14,'0','2024-09-20','0',NULL,'1','Rt.hemiplegia d/t Cb.infarction (Lt. BG & CR) ','0','2','2','2025-08-08 15:40:20',NULL),('5066',1,'마이크로','2025-03-29','구혜영',58,9,'0','2024-10-07','1',NULL,'1','Rt.hemiplegia d/t ICH, IVH  ','0','2','2','2025-08-08 15:40:20',NULL),('5067',1,'마이크로','2025-03-29','구혜영',47,12,'0','2024-08-24','0',NULL,'1','Lt hemiplegia d/t infarction','1','2','2','2025-08-08 15:40:20',NULL);
/*!40000 ALTER TABLE `assess_lst` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-08-22 12:56:31
