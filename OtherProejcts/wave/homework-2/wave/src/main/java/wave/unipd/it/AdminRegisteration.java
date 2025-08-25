package wave.unipd.it;

import java.io.IOException;
import java.io.PrintWriter;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.util.logging.Logger;

import javax.servlet.RequestDispatcher;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

/**
 * Servlet implementation class AdminRegisteration
 */
@WebServlet("/register")
public class AdminRegisteration extends HttpServlet {
	private static final long serialVersionUID = 1L;
	
	private static final Logger logger = Logger.getLogger(CreateCustomerServlet.class.getName());
       

	protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		
		
//		PrintWriter out = response.getWriter();
//		out.print("working");
		
		String name = request.getParameter("username");
		String email = request.getParameter("email");
		String password = request.getParameter("password");
		String phone_no = request.getParameter("contact");
		
		RequestDispatcher dispatcher = null;
		
//		PrintWriter out = response.getWriter();
//		out.print(uname);
//		out.print(email);
//		out.print(pass);
//		out.print(contact);
		
		Connection con = null;
		try {
		Class.forName("org.postgresql.Driver");
		con = DriverManager.getConnection("jdbc:postgresql://localhost:5432/wave","postgres","Hacker082@");
		PreparedStatement pst = con.prepareStatement("INSERT INTO admin(name, email, password, phone_no) values(?,?,?,?)");
		
		pst.setString(1, name);
		pst.setString(2, email);
		pst.setString(3, password);
		pst.setString(4, phone_no);
		
		//this method will effect the row count(will count rows)
		int rowCount = pst.executeUpdate();
		
		dispatcher = request.getRequestDispatcher("AdminRegisteration.jsp");
		
		if(rowCount > 0) {
			request.setAttribute("status", "success");
		}else
		{
			request.setAttribute("status", "failed");
		}
		
		dispatcher.forward(request, response);
		
		
		
	}catch(Exception e) {
		e.printStackTrace();
		
	}finally {
		try {
			if(con != null) {
				con.close();
				logger.info("It will disconnect from DB.");
				System.out.println("Disconnected from the PostgreSQL database.");
			}
			
		} catch (SQLException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
		
	}

}
