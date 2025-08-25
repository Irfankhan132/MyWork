package wave.unipd.it;

import java.io.IOException;
import java.io.PrintWriter;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;

import javax.servlet.RequestDispatcher;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

/**
 * Servlet implementation class DeleteProductServlet
 */
@WebServlet("/deleteProduct")
public class DeleteProductServlet extends HttpServlet {
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
				String id = req.getParameter("p_id");
				
				
				try {
					
					Class.forName("org.postgresql.Driver");
					con = DriverManager.getConnection("jdbc:postgresql://localhost:5432/wave","postgres","Hacker082@");
					PreparedStatement pst = con.prepareStatement("DELETE from products WHERE p_id = ?");
					
					pst.setString(1, id);
					
					int count = pst.executeUpdate();
					
					if(count == 1) {
						pw.println("<h2> Record is deleted successfully</h2>");
					}else {
						pw.println("<h2> Record is not deleted.</h2>");
					}
				
					
				} catch (Exception e) {
					e.printStackTrace();
				}finally {
					try {
						
						if(con != null) {
							con.close();
							System.out.println("connected from the PostgreSQL database.");
						}
						
					} catch (Exception e2) {
						// TODO: handle exception
						e2.printStackTrace();
					}
				}
				
				pw.println("<a href = 'index.jsp'> Home Page</a>");
				pw.println("<br>");
				pw.println("<a href = 'ProductList'> Product List </a>");
		
	}

	/**
	 * @see HttpServlet#doPost(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		// TODO Auto-generated method stub
		doGet(request, response);
	}

}
