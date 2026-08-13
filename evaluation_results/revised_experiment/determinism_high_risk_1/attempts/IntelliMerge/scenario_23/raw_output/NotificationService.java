public class NotificationService {

    private Logger logger = Logger.getLogger(NotificationService.class.getName());
    
    public void sendNotification(String message, String recipient, String type) {
<<<<<<< ours
        NotificationStrategy strategy = strategies.get(type);
        if (strategy != null) {
            strategy.send(message, recipient);
=======
        logger.info("Iniciando envio de notificação tipo: " + type);
            
        try {
            // Ainda mantém lógica monolítica (RIGHT não introduziu Strategy)
            if ("EMAIL".equals(type)) {
                System.out.println("Enviando email para: " + recipient);
                System.out.println("Conteúdo: " + message);
                logger.info("Email enviado com sucesso para: " + recipient);
            } else if ("SMS".equals(type)) {
                System.out.println("Enviando SMS para: " + recipient);
                System.out.println("Texto: " + message);
                logger.info("SMS enviado com sucesso para: " + recipient);
            } else if ("PUSH".equals(type)) {
                System.out.println("Enviando push notification para: " + recipient);
                System.out.println("Mensagem: " + message);
                logger.info("Push notification enviado para: " + recipient);
            }
        } catch (Exception e) {
            logger.severe("Erro ao enviar notificação: " + e.getMessage());
            throw e;
>>>>>>> theirs
        }
    }
    private Map<String, NotificationStrategy> strategies;
    
    public NotificationService() {
        strategies = new HashMap<>();
        strategies.put("EMAIL", new EmailStrategy());
        strategies.put("SMS", new SmsStrategy());
        strategies.put("PUSH", new PushStrategy());
    }
    
}