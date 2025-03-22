-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Feb 27, 2025 at 12:44 AM
-- Server version: 10.4.27-MariaDB
-- PHP Version: 8.2.0

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `diemdanhsv`
--

-- --------------------------------------------------------

--
-- Table structure for table `dangky`
--

CREATE TABLE `dangky` (
  `HOCKY` varchar(50) DEFAULT NULL,
  `NIENKHOA` varchar(50) DEFAULT NULL,
  `DIEM1` decimal(10,2) DEFAULT NULL,
  `DIEM2` decimal(10,2) DEFAULT NULL,
  `KETQUA` decimal(10,2) DEFAULT NULL,
  `ID_SINHVIEN` int(11) NOT NULL,
  `ID_MON` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `dangky`
--

INSERT INTO `dangky` (`HOCKY`, `NIENKHOA`, `DIEM1`, `DIEM2`, `KETQUA`, `ID_SINHVIEN`, `ID_MON`) VALUES
('k1', '1', '10.00', '2.00', '4.40', 21, 19),
('hk1', 'hk1', '10.00', '10.00', '10.00', 24, 16),
('hk1', 'd', '10.00', '6.00', '7.20', 32, 20);

-- --------------------------------------------------------

--
-- Table structure for table `diemdanh`
--

CREATE TABLE `diemdanh` (
  `ID_DIEMDANH` int(11) NOT NULL,
  `ID_SINHVIEN` int(11) DEFAULT NULL,
  `ID_GIANGDAY` int(11) DEFAULT NULL,
  `NGAYDIEMDANH` datetime DEFAULT NULL,
  `TIET` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `diemdanh`
--

INSERT INTO `diemdanh` (`ID_DIEMDANH`, `ID_SINHVIEN`, `ID_GIANGDAY`, `NGAYDIEMDANH`, `TIET`) VALUES
(2, 31, 9, '2025-02-26 00:29:42', NULL),
(3, 31, 4, '2025-02-27 06:41:36', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `giangday`
--

CREATE TABLE `giangday` (
  `ID_GIANGDAY` int(11) NOT NULL,
  `NGAYDAY` date DEFAULT NULL,
  `TIETGD` varchar(100) DEFAULT NULL,
  `ID_GIAOVIEN` int(11) DEFAULT NULL,
  `ID_MON` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `giangday`
--

INSERT INTO `giangday` (`ID_GIANGDAY`, `NGAYDAY`, `TIETGD`, `ID_GIAOVIEN`, `ID_MON`) VALUES
(2, '2025-02-15', '1-2', 2, 16),
(3, '2025-02-15', '1-2', 2, 19),
(4, '2025-02-16', '1-2', 2, 19),
(5, '2025-02-15', '3 - 4', 2, 17),
(6, '2025-02-03', '3-4', 3, 18),
(7, '2025-02-03', '4-5', 5, 18),
(8, '2025-02-25', '4-6', 6, 18),
(9, '2025-02-20', '4-5', 4, 20);

-- --------------------------------------------------------

--
-- Table structure for table `giaovien`
--

CREATE TABLE `giaovien` (
  `ID_GIAOVIEN` int(11) NOT NULL,
  `TENGIAOVIEN` varchar(500) DEFAULT NULL,
  `ID_KHOA` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `giaovien`
--

INSERT INTO `giaovien` (`ID_GIAOVIEN`, `TENGIAOVIEN`, `ID_KHOA`) VALUES
(1, 'giáo viên 1', 3),
(2, 'giáo viên 2', 4),
(3, 'giáo viên 3', 1),
(4, 'giáo viên 5', 1),
(5, 'giáo viên 4', 2),
(6, 'giáo viên 6', 5),
(7, 'giáo viên 7', 2);

-- --------------------------------------------------------

--
-- Table structure for table `khoa`
--

CREATE TABLE `khoa` (
  `ID_KHOA` int(11) NOT NULL,
  `TENKHOA` varchar(200) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `khoa`
--

INSERT INTO `khoa` (`ID_KHOA`, `TENKHOA`) VALUES
(1, 'Kỹ thuật - công nghệ'),
(2, 'Quản Trị Kinh Doanh'),
(3, 'Ngoại Ngữ'),
(4, 'Tài Chính Ngấn Hàng'),
(5, 'Dược - Điều Dưỡng');

-- --------------------------------------------------------

--
-- Table structure for table `lophoc`
--

CREATE TABLE `lophoc` (
  `ID_LOP` int(11) NOT NULL,
  `TENLOP` varchar(200) DEFAULT NULL,
  `ID_KHOA` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `lophoc`
--

INSERT INTO `lophoc` (`ID_LOP`, `TENLOP`, `ID_KHOA`) VALUES
(3, 'Lớp 5', 1),
(4, 'Lớp 2', 1),
(5, 'lớp 3', 1),
(6, 'Lớp 1', 1),
(7, 'Lớp 4', 1);

-- --------------------------------------------------------

--
-- Table structure for table `lophoc_monhoc`
--

CREATE TABLE `lophoc_monhoc` (
  `ID_LOP` int(11) NOT NULL,
  `ID_MON` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `lophoc_monhoc`
--

INSERT INTO `lophoc_monhoc` (`ID_LOP`, `ID_MON`) VALUES
(3, 16),
(3, 18),
(4, 19),
(5, 17),
(6, 20),
(7, 21);

-- --------------------------------------------------------

--
-- Table structure for table `monhoc`
--

CREATE TABLE `monhoc` (
  `ID_MON` int(11) NOT NULL,
  `TENMON` varchar(200) DEFAULT NULL,
  `SOTINCHI` int(11) DEFAULT NULL,
  `ID_GIAOVIEN` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `monhoc`
--

INSERT INTO `monhoc` (`ID_MON`, `TENMON`, `SOTINCHI`, `ID_GIAOVIEN`) VALUES
(16, 'Toán số', 3, 1),
(17, 'Toán hình', 3, 1),
(18, 'Toán xác suất', 2, 2),
(19, 'luật', 2, 3),
(20, 'Quốc phòng', 8, 4),
(21, 'Nguyên Lý Máy Học', 4, 2);

-- --------------------------------------------------------

--
-- Table structure for table `sinhvien`
--

CREATE TABLE `sinhvien` (
  `ID_SINHVIEN` int(11) NOT NULL,
  `TENSINHVIEN` varchar(200) DEFAULT NULL,
  `NGAYSINH` date DEFAULT NULL,
  `GIOITINH` int(1) DEFAULT NULL,
  `ID_LOP` int(11) DEFAULT NULL,
  `KHUONMAT` longblob DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `sinhvien`
--

INSERT INTO `sinhvien` (`ID_SINHVIEN`, `TENSINHVIEN`, `NGAYSINH`, `GIOITINH`, `ID_LOP`, `KHUONMAT`) VALUES
(20, 'đãm', '2025-02-25', 1, 6, NULL),
(21, 'muông', '2025-02-05', 1, 4, 0xabaaaaaa0e26c5bfe4388ec30a43bb3fc7711ca71903b33fc7711c77840ab2bfe4388e83c15dbdbf1cc771fcbfadbabf721cc7d162f3b5bf721cc7512957c2bfc7711c670d52bb3fabaaaa8a5fa4bdbfc7711c276956cf3fabaaaada77f8c0bf8ee3382e9647cabfabaaaa0a26d6b3bf398ee378c19fa9bf555555959ba8c63fc7711c4760b2c7bf555555d52a6dbbbf398ee368b46687bfc7711c1728e08fbf721cc7d1b148b83fc7711ce7d09fafbf555555f5058b843fe4388ea3bd84a23f00000000b0cbc1bf000000200c8fd5bfabaaaadaf85ab3bf000000c0ff29abbfe4388e8382c3823f55555595bf8e97bf721cc7515cb2a1bf00000060cd5b983fc7711c871856cdbf721cc71161c0b1bf8ee3382e35e3723fabaaaaea9c0eb73f555555fdc92c7c3fe4388ef3c44b82bf1cc7719c0737bf3f398ee3b8a87faabf721cc7d1ef2ed1bf000000c0bda2a5bf398ee348767ab23fe4388e039d17cb3fabaaaaca412fc43f000000c0287cb53f721cc76183a79c3f721cc7a18c62c2bfc7711cc70f17bd3fe4388e73e791c0bfe4388e6b6949a33f1cc771bc5016c23f55555595a4ceaa3f398ee3d8e3639e3f000000a01703753f0000009070b0c0bf8ee338cedb8ba03fe4388ea3095fc53f721cc7119509bcbfc7711cc78768a43f398ee3284257c13f000000004acfaabfc7711cc73dc97ebfabaaaa8ac694bbbf55555555db43d13f721cc7f1da30aa3f555555f552a9c3bf398ee3f8de2cc1bf398ee338bcf9bd3f1cc7718c9c26c0bf555555f5950fb2bf555555554659a23f8ee3384e82a2c0bfabaaaaea4f35c8bf555555d5c8d8d7bf0000002012a989bf398ee3583581d53f721cc7b1e662b73f1cc7717c8a9bc6bf1cc771dc0316a23f721cc721c4e8a6bfc7711c17ae8a843f721cc7719c83c13f000000e01f3dc93f721cc771757796bf721cc731fc82b53f000000e042deafbfc7711c27e017a5bf0000008059a9cc3fc7711c87b27aabbf000000c4c3ff833fc7711ce78cf0cd3f000000901193a3bf721cc7d14d1bac3fc7711c57b0009abfabaaaa7a0f72913f398ee338434dc0bf5555559537f4743f00000040773fbabfe4388e63e8109cbf8ee3389ef3969d3fe4388e2311a4acbf555555b979da96bf000000301802c03f1cc7713cc844c8bfe4388ea37f32bb3fc7711c8769797cbf8ee3384e8cddb63fc7711cc7e7f572bf1cc771047026753fabaaaaca4c36a6bf8ee338ee7888bbbf555555b5eb37b93f1cc7715c68bfc8bfabaaaaeafeb1c83f5555555573fdca3f1cc7719ca3b4b53f1cc7711cb4bfbc3f721cc71173d3c43f721cc75147dbad3f1cc771acddb2963fabaaaa3abd059b3fc7711c879b06c5bfc7711c5be6c973bf398ee318f495b53f721cc771b26eb9bf8ee338ceffd8b83fc7711ce711c9883f),
(22, 'đãm', '2025-02-12', 1, 5, 0x33333323ed97c6bf000000d06805b83fcdcccca409f0b13f333333935cf6b4bf66666656e9d4bdbf000000d01b6fb9bf9a9999895e61b4bf333333a3bf7ac2bf333333c3b4a8bf3fcdcccc34eb5bc0bf3333334393bdce3f6666665e2a9bc0bf33333383ab7ec9bf666666669d77b1bf333333338d5aafbf9a99994989cdc63f333333a33690c4bf9a9999594f91bcbf00000020096486bf000000e0203489bf0000002061ceb83f9a9999095fcca8bf666666767837673f000000805909a23f666666560209c7bf000000b08895d5bf6666662641c4b4bf333333fbf57ba4bf000000b005599fbf666666e6410e9cbf666666b650dc8fbfcdcccce8fed4a03f9a9999f1f577d0bf000000a87525b3bf333333d31b31813f3333332bd8f3b33fcdccccfc86ea863f9a999939ebfa82bf00000078fd61c03f9a999961381fa0bf000000500727d1bfcdcccc4c40659fbf33333323c9cfb23f9a999909e8d4cb3f666666e6eb24c13f6666663606b7af3f333333c3106fa13f666666768dafc3bf33333303d7b4be3fcdccccec72d6c0bfcdcccc8ced30863f9a9999c91851c03f9a9999856d54a33f6666664eb75f9b3f9a999989541b823f9a9999d9cab6bbbf000000301179a53f00000000a393c63f9a9999397648bebf3333334398b0a93f9a999949d255be3f00000040b512b1bf9a9999d9d93694bf9a9999a9ab76bdbf666666ee9856d03f000000e8ab06a63fcdcccc5c67a4c2bf00000080475dc2bfcdcccc9c4f6cbd3fcdcccc5ca0aababf666666b6b1fdb0bf9a99997913f4a53f33333343ece9bebf00000060566fcabf9a9999a97fa8d8bfcdcccc0c29ef64bf666666367b14d63fcdccccac02aab83f9a9999e9d6dac6bf9a9999f9b998af3f3333337394c2a6bfcdccccec2f60923fcdcccc7c673bc03f333333a35d41c83f33333343988480bf9a999959045fb73f9a999959d3e1a3bf9a9999e9c7528cbf000000d06d72ce3f333333bb23fda6bfcdcccccc0936623f666666d6a5becd3f666666729800a8bf333333430c4bab3f9a9999f991089cbfcdcccc08017f963f666666f67f21c2bfcdccccb83d4e8a3f000000808e30b5bfcdccccb4adfe83bf00000098e048a83f333333839607a8bf6666666600ca393fcdcccc7418d1c03f9a9999b9cbc2c9bf000000e0f3f3be3f3333333339ea91bf666666b659e4b13f66666606576871bf000000198394963f333333936fe8a4bf666666d6fe53b7bf00000070b06ab33f66666646400eccbf9a999919058aca3f000000106c77c93fcdcccc1c8b4aad3f9a9999999662bf3f9a99991980d8c33f000000683382a73f3333337357a8913f9a9999c9f859ad3fcdccccdc53c0c3bf000000c8126799bfcdccccdc6703b83f66666676675bb7bf333333c3336bbe3fcdcccc8c5f086c3f),
(23, 'tới', '2025-02-10', 2, 7, NULL),
(24, 'tới', '2025-02-20', 0, 3, NULL),
(31, 'nvdam', '2025-02-04', 2, 4, 0x6666665607f2c9bf6666661e1179c03f6666660e1c97b23f333333f30cb6b7bf333333930d5dbfbfcdcccc3ccd2cbbbf66666646488bb5bf666666debe1ec1bfcdcccc1c61a6bb3f666666263db0bdbfcdcccc7c2037ce3f9a9999b1a120c2bfcdccccec88ddccbf666666d633a2afbf66666686e232b2bf333333e35333c93f66666686c273c9bf9a999959c788bdbf66666646b2e197bf666666ce99758dbfcdccccac81d6bf3f333333c5c25f8bbf9a9999794eb7893f00000060e1268e3f333333a3d2fec3bf00000070861cd9bf000000102e8ab8bf66666666a0c8a6bf3333339382269fbf9a999971186398bfcdcccc3c785d90bf666666767120693fcdcccc4c39f6cbbf9a999929eabdaebfcdcccc3c65e7853f333333a34926b83f0000004e925e8f3f333333835adca7bfcdcccc2cf902bc3fcdcccca87ad397bf3333337318bdd1bfcdcccc7428139ebf000000707136bb3f666666169182cc3f9a9999996600c53fcdcccc047314b33f00000068c02ca13f6666662683cac1bf00000040f062b83f3333336b520ec1bfcdcccc4cb0197f3f000000c05347be3f9a9999b900ad9b3fcdcccc9c860fa43f000000f01ab29f3f9a99994984dfb2bf3333338be983a53fcdcccc2c1afcc43f9a999909d8b2c1bf0000004ca40787bfcdcccc6c6f6cc03f666666e6edd0afbf33333313bae476bfcdcccc8c44d4b7bf00000010ad0ad23f6666660669caab3fcdcccc8cc81ac3bf000000204b15c1bf9a99990911f7c03f000000584b2fc0bf666666365b45b6bf9a9999a99303a23fcdccccec7e19bfbf9a9999097bf2c6bf66666666f135d7bf33333373f5c86c3f666666762fbed83f333333d3e39db73f33333373c683c3bf00000050831ea93f000000a02093a8bf333333334e4a59bf666666c6db83c23f9a9999d964bfc83f9a9999d9c5056abf6666660e9982b33f0000001859e2b2bf33333323008689bf6666660e3b29d03f3333338302f2abbf9a9999f77bda87bf000000405ab9cd3fcdcccc9cf4c78abf333333e3db60ac3f66666666c56469bf6666669636bfa03f333333839822c1bf666666460701603f66666606fe23b7bf333333afeb289cbf333333c327b2a63f9a9999617a109ebf0000009870b4a1bfcdccccdc2be2c03fcdcccc4c614ec4bf33333383fddfb73f0000004099d158bf9a99990982a5a73fcdcccc94b66f93bf6666663e4b91643f666666c6a3c899bf9a9999597a4ebbbf333333f3f17baf3fcdcccccc9819cbbf6666661609acc53f000000e0c928ca3f000000e889ddaa3fcdccccbcd49cbf3f6666661e996fc13f9a99991580d6a33fcdcccc4c6ead963f6666666e5e1f9a3f666666967950c4bf6666668e4b93a1bf000000e08138b83f33333389d33daebf666666a6be45be3f000000c0114f5c3f),
(32, 'Nguyễn Văn Đãm', '2025-02-12', 1, 6, 0x333333c3db31c8bf333333f3465dba3f66666686b16bae3f66666656d5e0b6bf9a9999d9c0dcbfbf000000f068ddbbbf33333333b5ceb5bf66666606ecaec4bf333333dba97cc03f6666665e8931c0bf000000e057fecf3f9a9999990a8cc0bf333333e3e993c7bf000000d0b164b4bf9a999971cc0eb4bf333333e34913c83fcdcccc2c1bc8c6bf000000c07f8abcbf333333930e1487bf9a9999c1b86081bfcdcccc7ce450b83f9a9999fd66dd9cbf000000c0bf1a683f6666663abe10a63f9a9999c9d171c6bf00000030e5d6d5bf6666661e5c50b5bf666666c6bfa5aabf000000008e19a2bf3333336f408087bf33333383294f88bf6666667aaa6ba63fcdcccccc2f2bd0bf000000204cf3b5bf00000000bf5d8b3fcdcccc24f5a7b33fcdcccc083b3c813f9a99995108e283bf9a9999d1acf6c03f9a9999d92a73a6bf9a9999b9d7e5d0bf0000007821e799bf333333331c7bb73f33333343b110cd3f9a999971f913c13fcdcccc8c3a97ae3fcdccccf43b86a13f0000002092b5c2bf333333d395fbbe3f9a999989669dc0bfcdcccc0c5b7f613fcdcccc0cd990be3f666666267edba83f6666665e9c72943f000000b0657d893f00000060d765bbbf000000a882fda53f666666262190c73f000000d06f6dbfbfcdccccb0427fa23f9a999919d6aabc3fcdccccd82f35b2bf00000014a54d94bfcdccccfc381cbdbf333333430893d03f9a9999917b2aab3f666666564765c1bf9a9999093f85c0bf666666669c8abe3f00000010cca0b9bf66666686ec96b2bf0000004042bca13f66666696c08ec0bf333333338c49cabf33333323fee6d8bf000000b0ded68dbfcdccccecda0dd73f9a9999a938b2b83f000000e0d198c5bfcdccccc4fe88b03f333333d33b699bbf0000005002d0963f6666662667d8c03fcdccccec79dfc63fcdccccecb0ff8ebf666666ee8743b33f6666668ee65ea4bf666666267cab7abf000000804d85ce3fcdccccfc8f47a6bf9a9999693a8c50bf33333393756bcc3f9a9999c935c5a4bf9a9999a905bca83f00000070481e9cbfcdccccc0eb24823f9a9999095cb2bfbfcdcccc8cbfba913f6666661e74f0b3bf6666660ed32c873f33333303faa1a63f9a999905346fa2bfcdccccccbf3e483f666666de5db1c03f000000b0c919c9bfcdcccccc3c5fbb3fcdcccc08b03481bf6666665e7ff6b03f000000b076c182bf6666667c0418983f666666caaf6ca0bf666666b68dccb5bf666666a60751b33f9a999959cf35cabf666666465d52cb3f33333373a640c83f6666660e4e0fa63f33333383decac13fcdcccc64cb30c23fcdccccd420d4a33f66666666521a7c3f333333d3fc41ab3f33333373827fc4bf333333dbedb3a1bf666666e66379bc3fcdcccc9c8171b8bf666666d62dccc13fcdccccdc6cba763f);

-- --------------------------------------------------------

--
-- Table structure for table `taikhoangv`
--

CREATE TABLE `taikhoangv` (
  `ID_TKGV` int(11) NOT NULL,
  `USERNAME` varchar(200) DEFAULT NULL,
  `PASSWORD` varchar(200) DEFAULT NULL,
  `QUYENHAN` varchar(200) DEFAULT NULL,
  `ID_GIAOVIEN` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `taikhoangv`
--

INSERT INTO `taikhoangv` (`ID_TKGV`, `USERNAME`, `PASSWORD`, `QUYENHAN`, `ID_GIAOVIEN`) VALUES
(1, 'hovtoi', '12345', 'teacher', 1),
(2, 'toi', 'toi', '0', 2);

-- --------------------------------------------------------

--
-- Table structure for table `taikhoansv`
--

CREATE TABLE `taikhoansv` (
  `ID_TKSV` int(11) NOT NULL,
  `USERNAME` varchar(200) DEFAULT NULL,
  `PASSWORD` varchar(200) DEFAULT NULL,
  `ID_SINHVIEN` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `taikhoansv`
--

INSERT INTO `taikhoansv` (`ID_TKSV`, `USERNAME`, `PASSWORD`, `ID_SINHVIEN`) VALUES
(7, 'dam', 'dam', 32),
(8, 'nvdam', 'nvdam', 21),
(9, 'hovtoi', 'hovtoi', 24),
(10, 'goog', 'goog', 22);

-- --------------------------------------------------------

--
-- Table structure for table `thongbao`
--

CREATE TABLE `thongbao` (
  `id` int(11) NOT NULL,
  `tieude` varchar(255) DEFAULT NULL,
  `noidung` text DEFAULT NULL,
  `ngaydang` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `thongbao`
--

INSERT INTO `thongbao` (`id`, `tieude`, `noidung`, `ngaydang`) VALUES
(1, 'Thông báo 1', 'Nội dung thông báo 1', '2024-02-10'),
(2, 'Thông báo 2', 'Nội dung thông báo 2', '2024-02-09');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `dangky`
--
ALTER TABLE `dangky`
  ADD PRIMARY KEY (`ID_SINHVIEN`,`ID_MON`),
  ADD KEY `ID_MON` (`ID_MON`);

--
-- Indexes for table `diemdanh`
--
ALTER TABLE `diemdanh`
  ADD PRIMARY KEY (`ID_DIEMDANH`),
  ADD KEY `ID_SINHVIEN` (`ID_SINHVIEN`),
  ADD KEY `ID_GIANGDAY` (`ID_GIANGDAY`);

--
-- Indexes for table `giangday`
--
ALTER TABLE `giangday`
  ADD PRIMARY KEY (`ID_GIANGDAY`),
  ADD KEY `ID_GIAOVIEN` (`ID_GIAOVIEN`),
  ADD KEY `ID_MON` (`ID_MON`);

--
-- Indexes for table `giaovien`
--
ALTER TABLE `giaovien`
  ADD PRIMARY KEY (`ID_GIAOVIEN`),
  ADD KEY `ID_KHOA` (`ID_KHOA`);

--
-- Indexes for table `khoa`
--
ALTER TABLE `khoa`
  ADD PRIMARY KEY (`ID_KHOA`);

--
-- Indexes for table `lophoc`
--
ALTER TABLE `lophoc`
  ADD PRIMARY KEY (`ID_LOP`),
  ADD KEY `ID_KHOA` (`ID_KHOA`);

--
-- Indexes for table `lophoc_monhoc`
--
ALTER TABLE `lophoc_monhoc`
  ADD PRIMARY KEY (`ID_LOP`,`ID_MON`),
  ADD KEY `ID_MON` (`ID_MON`);

--
-- Indexes for table `monhoc`
--
ALTER TABLE `monhoc`
  ADD PRIMARY KEY (`ID_MON`),
  ADD KEY `fk_giaovien` (`ID_GIAOVIEN`);

--
-- Indexes for table `sinhvien`
--
ALTER TABLE `sinhvien`
  ADD PRIMARY KEY (`ID_SINHVIEN`),
  ADD KEY `fk_sinhvien_lophoc` (`ID_LOP`);

--
-- Indexes for table `taikhoangv`
--
ALTER TABLE `taikhoangv`
  ADD PRIMARY KEY (`ID_TKGV`),
  ADD KEY `ID_GIAOVIEN` (`ID_GIAOVIEN`);

--
-- Indexes for table `taikhoansv`
--
ALTER TABLE `taikhoansv`
  ADD PRIMARY KEY (`ID_TKSV`),
  ADD KEY `ID_SINHVIEN` (`ID_SINHVIEN`);

--
-- Indexes for table `thongbao`
--
ALTER TABLE `thongbao`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `diemdanh`
--
ALTER TABLE `diemdanh`
  MODIFY `ID_DIEMDANH` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `giangday`
--
ALTER TABLE `giangday`
  MODIFY `ID_GIANGDAY` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT for table `giaovien`
--
ALTER TABLE `giaovien`
  MODIFY `ID_GIAOVIEN` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `khoa`
--
ALTER TABLE `khoa`
  MODIFY `ID_KHOA` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `lophoc`
--
ALTER TABLE `lophoc`
  MODIFY `ID_LOP` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `monhoc`
--
ALTER TABLE `monhoc`
  MODIFY `ID_MON` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=22;

--
-- AUTO_INCREMENT for table `sinhvien`
--
ALTER TABLE `sinhvien`
  MODIFY `ID_SINHVIEN` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=33;

--
-- AUTO_INCREMENT for table `taikhoangv`
--
ALTER TABLE `taikhoangv`
  MODIFY `ID_TKGV` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `taikhoansv`
--
ALTER TABLE `taikhoansv`
  MODIFY `ID_TKSV` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `thongbao`
--
ALTER TABLE `thongbao`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `dangky`
--
ALTER TABLE `dangky`
  ADD CONSTRAINT `dangky_ibfk_1` FOREIGN KEY (`ID_SINHVIEN`) REFERENCES `sinhvien` (`ID_SINHVIEN`),
  ADD CONSTRAINT `dangky_ibfk_2` FOREIGN KEY (`ID_MON`) REFERENCES `monhoc` (`ID_MON`);

--
-- Constraints for table `diemdanh`
--
ALTER TABLE `diemdanh`
  ADD CONSTRAINT `diemdanh_ibfk_1` FOREIGN KEY (`ID_SINHVIEN`) REFERENCES `sinhvien` (`ID_SINHVIEN`),
  ADD CONSTRAINT `diemdanh_ibfk_2` FOREIGN KEY (`ID_GIANGDAY`) REFERENCES `giangday` (`ID_GIANGDAY`);

--
-- Constraints for table `giangday`
--
ALTER TABLE `giangday`
  ADD CONSTRAINT `giangday_ibfk_1` FOREIGN KEY (`ID_GIAOVIEN`) REFERENCES `giaovien` (`ID_GIAOVIEN`),
  ADD CONSTRAINT `giangday_ibfk_2` FOREIGN KEY (`ID_MON`) REFERENCES `monhoc` (`ID_MON`);

--
-- Constraints for table `giaovien`
--
ALTER TABLE `giaovien`
  ADD CONSTRAINT `giaovien_ibfk_1` FOREIGN KEY (`ID_KHOA`) REFERENCES `khoa` (`ID_KHOA`);

--
-- Constraints for table `lophoc`
--
ALTER TABLE `lophoc`
  ADD CONSTRAINT `lophoc_ibfk_1` FOREIGN KEY (`ID_KHOA`) REFERENCES `khoa` (`ID_KHOA`);

--
-- Constraints for table `lophoc_monhoc`
--
ALTER TABLE `lophoc_monhoc`
  ADD CONSTRAINT `lophoc_monhoc_ibfk_1` FOREIGN KEY (`ID_LOP`) REFERENCES `lophoc` (`ID_LOP`),
  ADD CONSTRAINT `lophoc_monhoc_ibfk_2` FOREIGN KEY (`ID_MON`) REFERENCES `monhoc` (`ID_MON`);

--
-- Constraints for table `monhoc`
--
ALTER TABLE `monhoc`
  ADD CONSTRAINT `fk_giaovien` FOREIGN KEY (`ID_GIAOVIEN`) REFERENCES `giaovien` (`ID_GIAOVIEN`) ON DELETE CASCADE;

--
-- Constraints for table `sinhvien`
--
ALTER TABLE `sinhvien`
  ADD CONSTRAINT `fk_sinhvien_lophoc` FOREIGN KEY (`ID_LOP`) REFERENCES `lophoc` (`ID_LOP`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `taikhoangv`
--
ALTER TABLE `taikhoangv`
  ADD CONSTRAINT `taikhoangv_ibfk_1` FOREIGN KEY (`ID_GIAOVIEN`) REFERENCES `giaovien` (`ID_GIAOVIEN`);

--
-- Constraints for table `taikhoansv`
--
ALTER TABLE `taikhoansv`
  ADD CONSTRAINT `taikhoansv_ibfk_1` FOREIGN KEY (`ID_SINHVIEN`) REFERENCES `sinhvien` (`ID_SINHVIEN`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
