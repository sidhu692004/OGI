import java.io.*;
import java.net.URL;
import java.net.URLConnection;

public class RunHello {
    public static void main(String[] args) {
        try {
            // Check internet connection
            URL url = new URL("https://www.google.com");
            URLConnection connection = url.openConnection();
            connection.connect();
            System.out.println("Connected to the internet successfully.");

            // Define the command to run the Python script
            String[] command = {"python", "C:\\Users\\Welcome\\Desktop\\OGI\\RunHello\\check.py"};
            Process process = null;

            try {
                // Execute the Python script
                process = Runtime.getRuntime().exec(command);
                System.out.println("Python script executed. Reading output...");

                // Capture the output of the Python script
                BufferedReader stdInput = new BufferedReader(new InputStreamReader(process.getInputStream()));
                BufferedReader stdError = new BufferedReader(new InputStreamReader(process.getErrorStream()));

                String s;
                System.out.println("Output from the Python script:");
                while ((s = stdInput.readLine()) != null) {
                    System.out.println(s);
                }

                System.out.println("Errors (if any) from the Python script:");
                while ((s = stdError.readLine()) != null) {
                    System.out.println(s);
                }
            } catch (IOException e) {
                System.err.println("Error while executing the Python script:");
                e.printStackTrace();
            } finally {
                if (process != null) {
                    process.destroy();
                }
            }
        } catch (Exception e) {
            System.out.println("Internet connection not available. Starting the game offline...");
            new GameFrame(); // Assuming `GameFrame` is part of your program
        }
    }
}
