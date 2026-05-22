public class NotificationService {
    
    public void sendNotification(String message, String recipient, String type) {
        // Lógica monolítica para todos os tipos de notificação
        if ("EMAIL".equals(type)) {
            System.out.println("Enviando email para: " + recipient);
            System.out.println("Conteúdo: " + message);
            // Lógica específica de email
        } else if ("SMS".equals(type)) {
            System.out.println("Enviando SMS para: " + recipient);
            System.out.println("Texto: " + message);
            // Lógica específica de SMS
        } else if ("PUSH".equals(type)) {
            System.out.println("Enviando push notification para: " + recipient);
            System.out.println("Mensagem: " + message);
            // Lógica específica de push notification
        }
    }
}