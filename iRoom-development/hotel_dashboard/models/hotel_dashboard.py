

from odoo import models, fields, api
from datetime import datetime,date, timedelta


class Hotel_dashboard(models.Model):
    _inherit = 'hotel.reservation'



    def search_reserve_room(self,room_id,cater_id,shop_id):
        room_id = int(room_id)
        cater_id = int(cater_id)
        shop_id = int(shop_id)
        categ_id = self.env['hotel.room_type'].search([('id','=',cater_id)])
        cat_id = categ_id.cat_id.id
        rooms = self.env['hotel.room'].search([('id','=',room_id)])
        room_id = rooms.product_id.id
        res = self.env['hotel.reservation.line'].search([
                ('room_number', '=', room_id),
                ('categ_id', '=', cat_id),
            ])
        reservation = []
        for i in res:
            reservation.append({
                'checkin': i.checkin,
                'checkout':i.checkout,
                'status':i.line_id.state,
                'id':i.line_id.id,
                'ref_no':i.line_id.reservation_no,
                'boolean':i.line_id.agent_id_boolean,
             })
        return reservation


    def search_folio(self,shop_id):
        shop_id = int(shop_id)
        fo = self.env['hotel_folio.line'].sudo().search([('folio_id.shop_id.id','=',shop_id)])
        folio = []
        for i in fo:
            folio.append({
                'checkin': i.checkin_date,
                'checkout':i.checkout_date,
                'status':i.folio_id.state,
                'id':i.id,
                'room_name':i.product_id.name,
                'fol_no':i.folio_id.reservation_id.reservation_no,
            })
        return folio

    def search_cleaning(self,shop_id):
        shop_id = int(shop_id)
        clean = self.env['hotel.housekeeping'].sudo().search([('room_no.shop_id.id','=',shop_id)])
        cleans = []
        for i in clean:
            cleans.append({
                'room_no':i.room_no.name,
                'checkin':i.current_date,
                'checkout':i.end_date,
                'id':i.id,
                'status':i.state,
            })
        return cleans

    def search_repair(self,shop_id):
        shop_id = int(shop_id)
        repair = self.env['rr.housekeeping'].sudo().search([('shop_id','=',shop_id)])
        repairs = []
        for i in repair:
            repairs.append({
                'room_no':i.room_no.name,
                'date':i.date,
                'id':i.id,
                'type':i.activity,
                'status':i.state,
            })
        return repairs

    def create_detail(self,room_type,room,checkin,checkout):
        date_obj = datetime.strptime(checkin, "%Y-%m-%d")
        check_in = date_obj.date()
        date2_date = datetime.strptime(checkout, "%Y-%m-%d")
        check_out = date2_date.date()
        #print('gggggggggggggggggggggggggggggggg',check_in,check_out)
        if check_in == check_out:
            check_out = check_out + timedelta(days=1)
        room_types = int(room_type)
        room = int(room)
        categ_id = self.env['hotel.room_type'].search([('id','=',room_types)])
        cat_id = categ_id.cat_id.id
        rooms = self.env['hotel.room'].search([('id','=',room)])
        price = rooms.list_price
        room_id = rooms.product_id.id
        detail=[{
            'room' :room_id,
            'cat_id' : cat_id,
            'price':price,
            'checkout':check_out,
            
        }]
        return detail

    def reserve_room(self,id):
        id = int(id)
        res=[]
        user = self.env.user
        reservation = self.env['hotel.reservation'].sudo().browse(id)
        if not user.partner_id.agent:
            res.append(
                {
                    'res_no':reservation.reservation_no,
                    'checkin':reservation.reservation_line.checkin,
                    'checkout':reservation.reservation_line.checkout,
                    'partner':reservation.partner_id.name,
                    'state':reservation.state,
                }
            )
            return res
        elif user.partner_id.agent and reservation.create_uid.id == user.id:
            res.append(
                {
                    'res_no':reservation.reservation_no,
                    'checkin':reservation.reservation_line.checkin,
                    'checkout':reservation.reservation_line.checkout,
                    'partner':reservation.partner_id.name,
                    'state':reservation.state,
                }
            )
            return res
        else:
            return res

    def folio_detail(self,id):
        id = int(id)
        res=[]
        user = self.env.user
        if not user.partner_id.agent:
            folio = self.env['hotel.folio'].browse(id)
            res.append(
                {
                    'res_no':folio.reservation_id.reservation_no,
                    'checkin':folio.room_lines.checkin_date,
                    'checkout':folio.room_lines.checkout_date,
                    'partner':folio.partner_id.name,
                    'state':folio.state,
                }
            )
            return res
        else:
            return res

    def cleaning_detail(self,id):
        id = int(id)
        res=[]
        user = self.env.user
        if not user.partner_id.agent:
            clean = self.env['hotel.housekeeping'].browse(id)
            res.append(
                {
                    'name':'Unavilable/Under Cleaning',
                    'start':clean.current_date,
                    'end':clean.end_date,
                    'inspector':clean.inspector.name,
                    'state':clean.state,
                }
            )
            return res
        else:
            return res

    def repair_repace_detail(self,id):
        id = int(id)
        res=[]
        user = self.env.user
        if not user.partner_id.agent:
            repair = self.env['rr.housekeeping'].browse(id)
            res.append(
                {
                    'name':'Repair/Repacement',
                    'date':repair.date,
                    'activity':repair.activity,
                    'request':repair.requested_by.name,
                    'approved':repair.approved_by,
                    'state':repair.state,
                }
            )
            return res
        else:
            return res
    
    # def check_agent(self,id):
    #     id = int(id)
    #     user = self.env.user
    #     if user.partner_id.agent:
    #         reservation = self.env['hotel.reservation'].search([('id', '=', id)])
    #         if reservation.agent_id == user.partner_id:
    #             return True
    #         else:
    #             return False
    #     else:
    #         return True
        
    def check_user(self):
        user = self.env.user
        if user.partner_id.agent:
            return False
        else:
            return True



    
    def get_datas(self,shop):
        shop_ids = int(shop)
        if shop_ids:
            check_in = self.env['hotel.reservation'].search([('state', '=', 'confirm'), ('shop_id', '=', shop_ids)])
            check_out = self.env['hotel.folio'].search([('state', '=','check_out'), ('shop_id', '=', shop_ids)])
            roomid = []
            room_id = self.env['hotel.room'].search([('shop_id','=',shop_ids)])
            for i in room_id:
                roomid.append(i)
            for i in room_id:
                book_his = self.env['hotel.room.booking.history'].search(
                    [('history_id', '=', i.id),('state', '!=', 'done'),('history_id.shop_id', '=',shop_ids )])
                if book_his and i in roomid:
                    roomid.remove(i)
            for i in room_id:
                prod = i.product_id.id
                housekeep = self.env['hotel.housekeeping'].search([('room_no','=',prod),('state', '!=', 'done'),('room_no.shop_id','=',shop_ids)])
                if housekeep and i in roomid:
                    roomid.remove(i)
            for i in room_id:
                repair = self.env['rr.housekeeping'].search([('room_no','=',i.id),('state', '!=', 'done'),('shop_id', '=', shop_ids)])
                if repair and i in roomid:
                    roomid.remove(i)
            booked = self.env['hotel.reservation'].search([('state', '!=', 'cancel'),('shop_id', '=', shop_ids)])
            
            return {
                'check_in': len(check_in),
                'check_out': len(check_out),
                'total': len(roomid),
                'booked': len(booked),
            }
        else:
            return {
                'check_in': '',
                'check_out': '',
                'total': '',
                'booked': '',
            }

    def get_view_reserve(self):
        view_id = self.env.ref('hotel_management.view_hotel_reservation_form1').id
        return view_id




class RoomType(models.Model):
    _inherit = 'hotel.room_type'




    def list_room_type(self,shop_id):
        current_user = self.env.user
        user_ids = self.env['res.users'].search([('id','=',current_user.id)])
        if user_ids.has_group('hotel_management.group_agent'):
            shop_id = int(shop_id)
            shop_id_agents = self.env['sale.shop'].search([("id","=",shop_id)])
            #current_user = self.env.user
            reservations =  self.env['hotel.reservation'].search([('create_uid','=',user_ids.id) and ('partner_id','=',user_ids.partner_id.id) and ('state','=','confirm')])
            #print("ggggggggggggggggggggggggggcccccccccccccccccxxxxxxxxxxx",reservations,user_ids)
            roomid_agent_categ = []
            for bookng in reservations:
                for room_id in bookng.reservation_line:
                    #print("ffffffffffvvvvvvvvvvvvvv",room_id.categ_id.name)
                    roomid_agent_categ.append(room_id.categ_id.name)
            types = self.env['hotel.room_type'].search([("name","in",roomid_agent_categ)])
            datas=[]
            for i in types:
                check = self.list_room(i.id,shop_id)
                #print("yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy",check)
                if check:
                    datas.append({
                    'name':i.name,
                    'id':i.id
                    })
            #print("list room typeeeeeeeeeeeeee",datas)
            return datas
        else:
            shop_id = int(shop_id)
            types = self.search([])
            data=[]
            for i in types:
                check = self.list_room(i.id,shop_id)
                if check:
                    data.append({
                    'name':i.name,
                    'id':i.id
                    })
            return data

    def list_room(self,res,shop_id):
        shop_id = int(shop_id)
        room_types =int(res)
        categ_id = self.env['hotel.room_type'].search([('id','=',room_types)])
        #print("77777777777777777777777777777777777777777",categ_id)
        current_user = self.env.user
        user_ids = self.env['res.users'].search([('id','=',current_user.id)])
        cat_id = categ_id.cat_id.id
        #print("pppppppppppppppppppppppppppppppppppp",cat_id)
        if user_ids.has_group('hotel_management.group_agent'):
                reservations =  self.env['hotel.reservation'].search([('create_uid','=',user_ids.id) and ('partner_id','=',user_ids.partner_id.id) and ('state','=','confirm')])
                roomid_agent = []
                roomid_agent_categ = []
                datas=[]
                for bookng in reservations:
                    for room_id in bookng.reservation_line:
                        #print("hhhhhhhhhhhhhhhhhhhhhhhhh",room_id.room_number.id)
                        roomid_agent.append(room_id.room_number.name)
                        roomid_agent_categ.append(room_id.categ_id.id)
                        product =  self.env['hotel.room'].search([('name','=',room_id.room_number.name)])
                room = self.env['hotel.room'].search([('name','in',roomid_agent),("shop_id","=",shop_id),('categ_id','=',cat_id)])
                
                for i in room:
                    #print("mikeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",i.categ_id.name)
                    datas.append({
                       'name':i.name,
                       'id':i.id,
                       'categ_id':i.categ_id.id,
                  })
                #print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",datas)
                return datas
        else:
            room = self.env['hotel.room'].search([('categ_id','=',cat_id),('shop_id','=',shop_id)])
            datas=[]
            for i in room:
                datas.append({
                    'name':i.name,
                    'id':i.id
                  })
            return datas


    def list_shop(self):
        res = []
        user = self.env.user
        if user.partner_id.agent:
            shop = self.env['agent.relation'].search([('agent_id','=',user.partner_id.id)])
            for i in shop:
              for s in i.shop_ids:
                res.append({
                        'name': s.name,
                        'id':s.id
                    })  
        else:
            shop = self.env['sale.shop'].search([])
            for i in shop:
                res.append({
                    'name': i.name,
                    'id':i.id
                })
        return res
    

    
        

    

