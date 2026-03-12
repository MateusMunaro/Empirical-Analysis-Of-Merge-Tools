
public class NotificationService {

<<<<<<< ./senarios_merge_base/JDime/scenario_23/left/notificationService.java
  private Map<String, NotificationStrategy> strategies;
=======
  private Logger logger = Logger.getLogger(NotificationService.class.getName());
>>>>>>> ./senarios_merge_base/JDime/scenario_23/right/notificationService.java


  public NotificationService() {
    strategies = new HashMap<>();
    strategies.put("EMAIL", new EmailStrategy());
    strategies.put("SMS", new SmsStrategy());
    strategies.put("PUSH", new PushStrategy());
  }

  public void sendNotification(String message, String recipient, String type) {

<<<<<<< ./senarios_merge_base/JDime/scenario_23/left/notificationService.java
    NotificationStrategy strategy = strategies.get(type);
=======
    logger.info("Iniciando envio de notifica\u00e7\u00e3o tipo: " + type);
>>>>>>> ./senarios_merge_base/JDime/scenario_23/right/notificationService.java


<<<<<<< ./senarios_merge_base/JDime/scenario_23/left/notificationService.java
    if (strategy != null) {
      strategy.send(message, recipient);
    }
=======
    try {
      if ("EMAIL".equals(type)) {
        System.out.println("Enviando email para: " + recipient);
        System.out.println("Conte\u00fado: " + message);
        logger.info("Email enviado com sucesso para: " + recipient);
      } else {
        if ("SMS".equals(type)) {
          System.out.println("Enviando SMS para: " + recipient);
          System.out.println("Texto: " + message);
          logger.info("SMS enviado com sucesso para: " + recipient);
        } else {
          if ("PUSH".equals(type)) {
            System.out.println("Enviando push notification para: " + recipient);
            System.out.println("Mensagem: " + message);
            logger.info("Push notification enviado para: " + recipient);
          }
        }
      }
    } catch (Exception e) {
      logger.severe("Erro ao enviar notifica\u00e7\u00e3o: " + e.getMessage());
      throw e;
    }
>>>>>>> ./senarios_merge_base/JDime/scenario_23/right/notificationService.java
  }
}