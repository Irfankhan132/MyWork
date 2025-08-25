package wave.unipd.it;

import java.util.logging.Logger;
import java.io.IOException;
import java.io.PrintWriter;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.util.logging.LogManager;
import java.util.logging.Logger;

import javax.servlet.RequestDispatcher;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.logging.log4j.message.StringFormatterMessageFactory;


@WebServlet("/addcustomerdata")
public class CreateCustomerServlet extends HttpServlet {
	

//	protected static final Logger LOGGER = LogManager.getLogger(CreateCustomerServlet.class,
//			StringFormatterMessageFactory.INSTANCE);
	private static final Logger logger = Logger.getLogger(CreateCustomerServlet.class.getName());
	
//	private static final Logger LOGGER = Logger.getLogger("CreateCustomerServlet");
	
	@Override
	protected void doGet(HttpServletRequest req, HttpServletResponse res) throws ServletException, IOException {
		
		
		//set content type
		res.setContentType("text/html");
		
		PrintWriter pw = res.getWriter();
		
		String customer_name = req.getParameter("name");
		String customer_email = req.getParameter("email");
		int customer_password = Integer.parseInt(req.getParameter("pass"));
		int customer_no = Integer.parseInt(req.getParameter("contact"));
		String customer_address = req.getParameter("address");
		
		RequestDispatcher dispatcher = null;
		
		Connection con = null;
		
		try {
			
			Class.forName("org.postgresql.Driver");
			con = DriverManager.getConnection("jdbc:postgresql://localhost:5432/wave","postgres","Hacker082@");
			PreparedStatement pst = con.prepareStatement("INSERT INTO customer(customer_name, customer_email, customer_password, "
					+ "customer_no, customer_address) values(?,?,?,?,?)");
			
			pst.setString(1, customer_name);
			pst.setString(2, customer_email);
			pst.setInt(3, customer_password);
			pst.setInt(4, customer_no);
			pst.setString(5, customer_address);
			
			//this method will effect the row count(will count rows)
			int rowCount = pst.executeUpdate();
			
			dispatcher = req.getRequestDispatcher("AddCustomers.jsp");
			
			if(rowCount > 0) {
				req.setAttribute("status", "success");
			}else
			{
				req.setAttribute("status", "failed");
			}
			
			dispatcher.forward(req, res);
			
		} catch (Exception e) {
			e.printStackTrace();
		}finally {
			try {
				
				if(con != null) {
					con.close();
					logger.info("It will disconnect from DB.");
					System.out.println("Disconnected from the PostgreSQL database.");
				}
				
			} catch (Exception e2) {
				// TODO: handle exception
				e2.printStackTrace();
			}
		}
		pw.println();
	}
	
	
	@Override
	protected void doPost(HttpServletRequest req, HttpServletResponse res) throws ServletException, IOException {
		
		doGet(req, res);
		
	}
}
