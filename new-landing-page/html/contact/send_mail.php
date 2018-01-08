<?php
require 'PHPMailer/PHPMailerAutoload.php';
require 'PHPMailer/extras/Security.php';

define('SMTP_HOST', 'smtp.mailgun.org'); // Hostname of the mail server
define('SMTP_USERNAME', 'postmaster@feebris.com'); // Username for SMTP authentication any valid email created in your domain
define('SMTP_PASSWORD', 'postmaster'); // Password for SMTP authentication
define('SMTP_PORT', 587); // Port of the SMTP like to be 25, 80, 465 or 587

// To address who will receive this email 
$to = 'corey@feebris.com';

$security = new Security();

// This IF condition is for improving security and Prevent Direct Access to the Mail Script.
if (isset($_POST['name']) AND isset($_POST['email']) AND isset($_POST['message']))
{    
    // Collect POST data from form
    $name = $security->xss_clean($_POST['name']);
    $email = $security->xss_clean($_POST['email']);
    $message = $security->xss_clean($_POST['message']);
    
    // Prefedined Variables  
    $set_from = 'Rinjani Notification Mailer';
    $subject = 'Rinjani: Message from ' . $name . '!';

    // Collecting all content in HTML Table
    $content = '<table width="100%">
    <tr><td colspan="2"><strong>Contact Details:</strong></td></tr>
    <tr><td valign="top">Name:</td><td>' . $name . '</td></tr>
    <tr><td valign="top">Email:</td><td>' . $email . '</td></tr>
    <tr><td valign="top">Message:</td><td>' . $message . '</td></tr>
    </table> ';
    
    $mail = new PHPMailer;
    $mail->isSMTP();
    $mail->SMTPDebug = 0;
    $mail->Debugoutput = 'html';
    $mail->Host = SMTP_HOST;
    //$mail->Port = SMTP_PORT;
    //$mail->SMTPSecure = 'tls';
    $mail->SMTPAutoTLS = false;
    $mail->SMTPAuth = TRUE;
    $mail->Username = SMTP_USERNAME;
    $mail->Password = SMTP_PASSWORD;
    
    $mail->setFrom(SMTP_USERNAME, $set_from);
    $mail->addAddress($to);

    $mail->Subject = $subject;
    $mail->msgHTML($content);
    
    // Send the message
    $send = false;
    if ($mail->send()) 
    {
        $send = true;
    }

    echo json_encode($send);
}