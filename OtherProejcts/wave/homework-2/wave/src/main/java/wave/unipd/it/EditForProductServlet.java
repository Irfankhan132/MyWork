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
 * Servlet implementation class EditForProductServlet
 */
@WebServlet("/EditProductURL")
public class EditForProductServlet extends HttpServlet {


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
		
		// now we need the edit data
		String p_name = req.getParameter("product_name");
		int p_price = Integer.parseInt(req.getParameter("product_price"));
		String p_categries = req.getParameter("product_categries");
		int p_size = Integer.parseInt(req.getParameter("product_size"));
		int p_quantity = Integer.parseInt(req.getParameter("product_quantity"));
		String p_description = req.getParameter("product_description");
		
		
		try {
			
			Class.forName("org.postgresql.Driver");
			con = DriverManager.getConnection("jdbc:postgresql://localhost:5432/wave","postgres","Hacker082@");
			PreparedStatement pst = con.prepareStatement("UPDATE products SET p_name=?, p_price=?, p_categries=?, "
					+ "p_size=?, p_quantity=?, p_description=? where p_id = ?");
			
			
			pst.setString(1, p_name);
			pst.setInt(2, p_price);
			pst.setString(3, p_categries);
			pst.setInt(4, p_size);
			pst.setInt(5, p_quantity);
			pst.setString(6, p_description);
			pst.setString(7, id);
			
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
