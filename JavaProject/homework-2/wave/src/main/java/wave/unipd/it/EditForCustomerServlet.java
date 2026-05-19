package wave.unipd.it;

import java.io.IOException;
import java.io.PrintWriter;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;

import javax.servlet.RequestDispatcher;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

/**
 * Servlet implementation class EditForCustomerServlet
 */
@WebServlet("/EditCustomerURL")
public class EditForCustomerServlet extends HttpServlet {
	private static final long serialVersionUID = 1L;

	/**
	 * @see HttpServlet#doGet(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doGet(HttpServletRequest req, HttpServletResponse res) throws ServletException, IOException {
		
				//set content type
				res.setContentType("text/html");
				PrintWriter pw = res.getWriter();
				
				RequestDispatcher dispatcher = null;
				
				Connection con = null;
				
				// get the name of the record
				String na = req.getParameter("customer_name");
				
				// now we need the edit data
				String customer_email = req.getParameter("customerEmail");
				int customer_password = Integer.parseInt(req.getParameter("customerPassword"));
				int customer_no = Integer.parseInt(req.getParameter("customerNumber"));
				String customer_address = req.getParameter("customerAddress");
				
				
				try {
					
					Class.forName("org.postgresql.Driver");
					con = DriverManager.getConnection("jdbc:postgresql://localhost:5432/wave","postgres","Hacker082@");
					PreparedStatement pst = con.prepareStatement("UPDATE customer SET customer_email=?, customer_password=?, "
							+ "customer_no=?, customer_address=? where customer_name = ?");
					
					
					pst.setString(1, customer_email);
					pst.setInt(2, customer_password);
					pst.setInt(3, customer_no);
					pst.setString(4, customer_address);
					pst.setString(5, na);
					
					int count = pst.executeUpdate();
					
					if(count == 1) {
						pw.println("<h2> Record is edited successfully</h2>");
					}else {
						pw.println("<h2> Record is not edited successfully</h2>");
					}
				
					
				} catch (Exception e) {
					e.printStackTrace();
				}finally {
					try {
						
						if(con != null) {
							con.close();
							System.out.println("Disconnected from the PostgreSQL database.");
						}
						
					} catch (Exception e2) {
						// TODO: handle exception
						e2.printStackTrace();
					}
				}
				
				pw.println("<a href = 'index.jsp'> Home Page</a>");
				pw.println("<br>");
				pw.println("<a href = 'CustomerList'> Book List </a>");
		
	}

	/**
	 * @see HttpServlet#doPost(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		// TODO Auto-generated method stub
		doGet(request, response);
	}

}
